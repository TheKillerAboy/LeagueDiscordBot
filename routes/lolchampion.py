import GLOBALS
import general

@GLOBALS.app.route('/lolchampion/<username>/<gateway>/<req_size>/<championId>/<channelId>/')
def lolchampion(username,gateway,req_size,championId,channelId):
    championId = int(championId)
    channelId = int(channelId)
    req_size = int(req_size)
    GLOBALS.client.loop.create_task(general.league_champion_embed_data_get(None,None,username,gateway,GLOBALS.client.get_channel(channelId),championId,queue=req_size,api_stack=2))
    return '''<!DOCTYPE HTML>
<HTML>
   <HEAD>
      <TITLE>Server Request</TITLE>
   </HEAD>
   <BODY>
      Request Pending...
      <script>setTimeout (window.close, 5000);</script>
   </BODY>
</HTML>'''