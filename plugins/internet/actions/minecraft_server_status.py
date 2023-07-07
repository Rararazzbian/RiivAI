import minestat

def run(server_ip):
    ms = minestat.MineStat(server_ip, 25565)
    info = []
    info.append('Minecraft server status of %s on port %d:' % (ms.address, ms.port))
    if ms.online:
      info.append('Server is online running version %s with %s out of %s players.' % (ms.version, ms.current_players, ms.max_players))
      # Bedrock-specific attribute:
      if ms.gamemode:
        info.append('Game mode: %s' % ms.gamemode)
      info.append('Message of the day: %s' % ms.motd)
      info.append('Message of the day without formatting: %s' % ms.stripped_motd)
      info.append('Latency: %sms' % ms.latency)
      info.append('Connected using protocol: %s' % ms.slp_protocol)
    else:
      info.append('Server is offline!')
    return info
