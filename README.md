# 740.wcpr.org

Extra functionality for WCPR that is hosted on-site.

## Setup

  1. Setup a virtualenv: `virtualenv env` (and activate: `env\Scripts\activate`)
  2. Install Python requirements: `pip install -r requirements.txt`
  
## Developing

1. Copy `flask_site\config\config_example.yml` to `flask_site\config\config.yml` and update
   as needed.
2. Run `env\Scripts\python start.py dev` to run a local Eventlet test server


## Deploy

1. `flask_site\config\config.yml` with production variables set must be copied to the
   production machine
2. `now_playing.ini` needs to be configured as the template for StationPlaylist output.
   In most cases, copy the file to `C:\Program Files (x86)\StationPlaylist\Studio\Templates`. 
   Thereafter, StationPlaylist should be configured to use that template and push the output
   to whatever `now_playing` is set to in `flask_site\config\config.yml`
3. Run `env\Scripts\start.py prod` on production machine to run a production-ready Eventlet server.
4. Configure GitHub webhooks to send a push event to `BASE_URL/webhook_receive` so that server will auto-update
    when a push to master is done.