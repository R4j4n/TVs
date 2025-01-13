import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from listallpis import scan_network_for_pis  # From previous artifact

app = FastAPI()


@app.get("/api/pis")
async def get_pis():
    pis = scan_network_for_pis()
    return {"pis": [{"name": name, "ip": ip} for name, ip in pis.items()]}


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Aerosports Trampoline</title>
        <style>
            :root {
                --primary: #2563eb;
                --background: #f8fafc;
            }
            
            body {
                font-family: system-ui, -apple-system, sans-serif;
                background: var(--background);
                margin: 0;
                padding: 2rem;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .header {
                text-align: center;
                margin-bottom: 3rem;
            }
            
            .logo {
                max-width: 200px;
                height: auto;
                margin-bottom: 1rem;
            }
            
            h1 {
                color: #1e293b;
                font-size: 2.5rem;
                margin: 1rem 0;
            }
            
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 1.5rem;
            }
            
            .card {
                background: white;
                border-radius: 1rem;
                padding: 1.5rem;
                box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
                transition: transform 0.2s, box-shadow 0.2s;
                cursor: pointer;
                border: 2px solid transparent;
            }
            
            .card:hover {
                transform: translateY(-4px);
                box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
                border-color: var(--primary);
            }
            
            .card h2 {
                color: #334155;
                margin: 0 0 0.5rem 0;
                font-size: 1.5rem;
            }
            
            .card p {
                color: #64748b;
                margin: 0;
            }
            
            .loading {
                text-align: center;
                color: #64748b;
                font-size: 1.2rem;
                padding: 2rem;
            }
            
            .error {
                background: #fee2e2;
                color: #991b1b;
                padding: 1rem;
                border-radius: 0.5rem;
                margin-bottom: 1rem;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .loading {
                animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
            }

            /* Customizable theme variables - modify these to change the look */
            :root {
                --primary-color: #2563eb;
                --background-color: #f8fafc;
                --card-background: white;
                --text-primary: #1e293b;
                --text-secondary: #64748b;
                --border-radius: 1rem;
                --animation-speed: 0.2s;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                
                <h1>Aerosports Media Manager</h1>
            </div>
            <div id="error" class="error" style="display: none;"></div>
            <div id="loading" class="loading">Looking for all Tv 👀...</div>
            <div id="grid" class="grid"></div>
        </div>
        
        <script>
            async function fetchPis() {
                try {
                    const response = await fetch('/api/pis');
                    if (!response.ok) throw new Error('Network scan failed');
                    
                    const data = await response.json();
                    document.getElementById('loading').style.display = 'none';
                    
                    const grid = document.getElementById('grid');
                    grid.innerHTML = '';
                    
                    data.pis.forEach(pi => {
                        const card = document.createElement('div');
                        card.className = 'card';
                        card.innerHTML = `
                            <h2>${pi.name}</h2>
                            <p>${pi.ip}</p>
                        `;
                        card.onclick = () => window.open(`http://${pi.ip}`, '_blank');
                        grid.appendChild(card);
                    });
                    
                    if (data.pis.length === 0) {
                        grid.innerHTML = '<p class="loading">No Pi devices found</p>';
                    }
                } catch (error) {
                    document.getElementById('loading').style.display = 'none';
                    const errorEl = document.getElementById('error');
                    errorEl.textContent = 'Failed to scan network: ' + error.message;
                    errorEl.style.display = 'block';
                }
            }
            
            fetchPis();
            setInterval(fetchPis, 30000);
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
