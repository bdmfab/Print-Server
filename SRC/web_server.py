from microdot import Microdot, Response
import params
import json
import re

app = Microdot()

@app.route('/')
async def index(request):
    """Serve the configuration page"""
    try:
        with open('index.html', 'r') as f:
            html = f.read()
        return Response(html, headers={'Content-Type': 'text/html'})
    except Exception as e:
        return Response('<html><body><h1>Error</h1><p>' + str(e) + '</p></body></html>', headers={'Content-Type': 'text/html'})

@app.route('/favicon')
async def favicon(request):
    """Serve the favicon"""
    try:
        with open('favicon.png', 'rb') as f:
            return Response(f.read(), headers={'Content-Type': 'image/png'})
    except:
        return Response('', status_code=404)

@app.route('/config')
async def get_config(request):
    """Return current configuration as JSON"""
    try:
        # Build ZPL data (skip first placeholder)
        zpl_data = []
        for zpl_list in params.zpl[1:]:
            zpl_data.append(list(zpl_list))
        
        # Check if date_time exists and is uncommented
        date_time_val = None
        if hasattr(params, 'date_time'):
            date_time_val = params.date_time
        
        return {
            'server_ip': params.serve_config[0],
            'subnet': params.serve_config[1],
            'gateway': params.serve_config[2],
            'dns': params.serve_config[3],
            'date_time': date_time_val,
            'sta': params.sta,
            'zpl': [None] + zpl_data  # Add None placeholder at start
        }
    except Exception as e:
        return {'error': str(e)}

@app.route('/save', methods=['POST'])
async def save_config(request):
    """Save the configuration to params.py"""
    try:
        data = request.json
        
        # Build new serve_config
        serve_config = (
            data.get('server_ip', '192.168.1.50'),
            data.get('subnet', '255.255.255.0'),
            data.get('gateway', '192.168.1.1'),
            data.get('dns', '8.8.8.8')
        )
        
        # Check if IP address changed
        ip_changed = serve_config[0] != params.serve_config[0]
        
        # Check if date_time should be set
        set_datetime = data.get('set_datetime') == 'on'
        date_time_tuple = None
        if set_datetime:
            date_time_tuple = (
                int(data.get('dt_year', 2026)),
                int(data.get('dt_month', 1)),
                int(data.get('dt_day', 1)),
                int(data.get('dt_weekday', 0)),
                int(data.get('dt_hour', 12)),
                int(data.get('dt_minute', 0)),
                int(data.get('dt_second', 0)),
                0  # subseconds always 0
            )
        
        # Build new sta list
        sta = []
        i = 1
        while f'sta_plc_{i}' in data:
            sta.append((
                data[f'sta_plc_{i}'],
                data[f'sta_printer_{i}'],
                int(data[f'sta_list_{i}']),
                data[f'sta_tag_{i}']
            ))
            i += 1
        
        # Build new zpl list
        zpl = [("Place Holder")]
        i = 1
        while True:
            # Check if this list exists
            if f'zpl_{i}_1' not in data:
                break
            
            # Build this ZPL list
            zpl_list = ["Place Holder"]
            j = 1
            while f'zpl_{i}_{j}' in data:
                zpl_list.append(data[f'zpl_{i}_{j}'])
                j += 1
            
            zpl.append(tuple(zpl_list))
            i += 1
        
        # Write the new params.py file
        with open('params.py', 'w') as f:
            f.write("# Format: (year, month, day, weekday, hours, minutes, seconds, subseconds)\n")
            f.write("# January 6, 2026, 8:42:00 PM (Tuesday, weekday=1)\n")
            f.write("# Uncomment and correct to set time...recomment after\n\n")
            
            if set_datetime and date_time_tuple:
                f.write(f"date_time = {repr(date_time_tuple)}\n\n")
            else:
                f.write("#date_time = (2026, 1, 6, 1, 20, 42, 0, 0)\n\n")
            
            f.write("        #         server_ip       subnet mask       gateway        dns\n")
            f.write(f"serve_config = {repr(serve_config)}\n\n")
            
            f.write("        #     plc_ip,  printer_ip, list num, tag\n")
            f.write("sta = [\n")
            for station in sta:
                f.write(f"       {repr(station)},\n")
            f.write("       ]\n\n")
            
            f.write("        # ZPL data for labels\n")
            f.write("zpl = [ (\"Place Holder\"),\n")
            for zpl_list in zpl[1:]:
                f.write(f"          {repr(zpl_list)},\n")
            f.write("          ]\n")
        
        # Reload the params module
        import sys
        if 'params' in sys.modules:
            del sys.modules['params']
        import params as new_params
        globals()['params'] = new_params
        
        return {
            'success': True, 
            'ip_changed': ip_changed,
            'new_ip': serve_config[0] if ip_changed else None
        }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/status')
async def status(request):
    """Return current configuration as JSON"""
    return {
        'serve_config': params.serve_config,
        'sta': params.sta,
        'zpl_count': len(params.zpl) - 1
    }

def run_server(host='0.0.0.0', port=80):
    """Start the web server"""
    print(f"Starting web server on http://{host}:{port}")
    print(f"Press ctl+c to access files")
    app.run(host=host, port=port, debug=True)

if __name__ == '__main__':
    run_server()
