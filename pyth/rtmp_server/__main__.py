import uvicorn

import os

uvicorn.run("rtmp_server.app:app", port=int(os.environ.get("PORT", 8000)), host="0.0.0.0")