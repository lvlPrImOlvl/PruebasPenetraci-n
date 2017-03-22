-- # Jonathan Soto JImenez
-- # Script para traceroute y geolocalizacion
-- # Modo de uso: nmap --traceroute --script ./TracerouteGeolocation.nse <ip>
-- # Ejemplo de uso y salida:
-- nmap --traceroute --script ./TracerouteGeolocation.nse 8.8.8.8
-- Starting Nmap 7.40 ( https://nmap.org ) at 2017-03-22 01:49 EDT
-- Nmap scan report for google-public-dns-a.google.com (8.8.8.8)
-- Host is up (0.047s latency).
-- Not shown: 999 filtered ports
-- PORT   STATE SERVICE
-- 53/tcp open  domain

-- Host script results:
-- | trace: 
-- |   HOP  RTT    ADDRESS                                                    GEOLOCATION
-- |   1    1.85   192.168.100.1                                              - ,- 
-- |   4    5.05   hu0-3-0-0.rcr21.mex01.atlas.cogentco.com (38.104.248.225)  37.751,-97.822 United States ()
-- |   5    17.40  be2692.rcr21.mfe02.atlas.cogentco.com (154.24.23.25)       37.751,-97.822 United States ()
-- |   6    26.74  be2888.ccr42.iah01.atlas.cogentco.com (154.54.47.45)       37.751,-97.822 United States ()
-- |   7    40.09  be2690.ccr42.atl01.atlas.cogentco.com (154.54.28.129)      37.751,-97.822 United States ()
-- |   8    42.11  be2790.ccr22.atl02.atlas.cogentco.com (154.54.27.166)      37.751,-97.822 United States ()
-- |   12   45.70  72.14.239.100                                              37.419,-122.057 United States (California)
-- |   13   46.14  216.239.63.88                                              37.419,-122.057 United States (California)
-- |_  23   50.78  google-public-dns-a.google.com (8.8.8.8)                   37.386,-122.084 United States (California)

local http = require "http"
local io = require "io"
local json = require "json"
local stdnse = require "stdnse"
local tab = require "tab"
local table = require "table"
local ipOps = require "ipOps"

description = [[
Lists the geographic locations of each hop in a traceroute and optionally
saves the results to a KML file, plottable on Google earth and maps.
]]

---
-- @usage
-- nmap --traceroute --script traceroute-geolocation
--
-- @output
-- | traceroute-geolocation:
-- |   hop  RTT     ADDRESS                                               GEOLOCATION
-- |   1    ...
-- |   2    ...
-- |   3    ...
-- |   4    ...
-- |   5    16.76   e4-0.barleymow.stk.router.colt.net (194.68.128.104)   62,15 Sweden (Unknown)
-- |   6    48.61   te0-0-2-0-crs1.FRA.router.colt.net (212.74.65.49)     54,-2 United Kingdom (Unknown)
-- |   7    57.16   87.241.37.146                                         42,12 Italy (Unknown)
-- |   8    157.85  212.162.64.146                                        42,12 Italy (Unknown)
-- |   9    ...
-- |_  10   ...
-- @xmloutput
-- <table>
--   <elem key="hop">1</elem>
-- </table>
-- <table>
--   <elem key="hop">2</elem>
-- </table>
-- <table>
--   <elem key="hop">3</elem>
-- </table>
-- <table>
--   <elem key="hop">4</elem>
-- </table>
-- <table>
--   <elem key="hop">5</elem>
--   <elem key="rtt">16.76</elem>
--   <elem key="ip">194.68.128.104</elem>
--   <elem key="hostname">e4-0.barleymow.stk.router.colt.net</elem>
--   <elem key="latitud">62</elem>
--   <elem key="longitud">15</elem>
-- </table>
-- <table>
--   <elem key="hop">6</elem>
--   <elem key="rtt">48.61</elem>
--   <elem key="ip">212.74.65.49</elem>
--   <elem key="hostname">te0-0-2-0-crs1.FRA.router.colt.net</elem>
--   <elem key="latitud">54</elem>
--   <elem key="longitud">-2</elem>
-- </table>

-- Variable que se creara con el nombre del programa.kmlfile
local arg_kmlfile = stdnse.get_script_args(SCRIPT_NAME .. ".kmlfile")

-- Creamos la funcion hostrule
hostrule = function(host)
  if ( not(host.traceroute) ) then
    return false
  end
  return true
end

--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
-- Creamos la funcion geoLookup, pasandole como parametros la ip y no_cache ----
-- no_cache definira cuando acaba el script-------------------------------- ----
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
local function geoLookup(ip, no_cache)
  -- Obtenemos el nombre del script y la ip, si alguna de ellas  no existe, regresa nil
  local output = stdnse.registry_get({SCRIPT_NAME, ip})
  if output then return output end

  -- Realizamos una consulta a geoplugin, concatenando la ip que estamos consultando
  local response = http.get("www.geoplugin.net", 80, "/json.gp?ip="..ip, {any_af=true})
  -- Parseamos los datos y obtenemos el estatus de la consulta y la localizacion
  local statusGet, location = json.parse(response.body)

  -- Si no esta definido statusGet, regresa nil y acaba
  if not statusGet then return nil end

  -- Obtenemos el nombre de la region o si esta vacio o es "Unknown" se pone Unknow
  local regionName = (location.geoplugin_regionName == json.NULL) and "Unknown" or location.geoplugin_regionName
  output =
  {
    latitud = location.geoplugin_latitude,
    longitud = location.geoplugin_longitude,
    region = regionName,
    country = location.geoplugin_countryName
  }
  -- Si la variable no_cache no tiene datos, agregara la salida al registro
  if not no_cache then
    stdnse.registry_add_table({SCRIPT_NAME}, ip, output)
  end
  return output
end

--------------------------------------------------------------------------------
--------- Variables locales donde se guardaran los datos de salida -------------
--------------------------------------------------------------------------------
local output_structured = {}
local output = tab.new(4)
local coordinates = {}


--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
------- Creamos la funcion output_hop, donde se hara la insercíon de los -------
-------------------- datos en una tabla estructurada ---------------------------
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
local function output_hop(count, ip, name, rtt, geolocation)
  -- Comprobamos que tenemos una ip
  if ip then
    -- Creamos la variable label, que tendra los datos con un formato en especifico
    -- por ejemplo, United States (California)
    local label
    if name then
      label = ("%s (%s)"):format(name or "", ip)
    else
      -- En caso de que no tenga nombre, el formato sera solo la ip
      label = ("%s"):format(ip)
    end

    -- Si la variable geolocation tiene datos, insertaremos los datos correspondientes
    if geolocation then
      table.insert(output_structured,
      { 
        hop = count,
        ip = ip,
        hostname = name,
        rtt = ("%.2f"):format(rtt),
        latitud = geolocation.latitud,
        longitud = geolocation.longitud
      })

      tab.addrow( output,
                  count,
                  ("%.2f"):format(rtt),
                  label,
                  ("%.3f,%.3f %s (%s)"):format(geolocation.latitud, geolocation.longitud, geolocation.country, geolocation.region)
                )

      table.insert(coordinates,
      {
        hop = count,
        latitud = geolocation.latitud,
        longitud = geolocation.longitud
      })
    else
      table.insert(output_structured,
        { 
        hop = count,
        ip = ip,
        hostname = name,
        rtt = ("%.2f"):format(rtt)
        })

      tab.addrow( output,
                  count,
                  ("%.2f"):format(rtt),
                  label,
                  ("%s,%s"):format("- ", "- ")
                )
    end
  else
    table.insert(output_structured, { hop = count })
    tab.addrow(output, count, "...")
  end
end


--------------------------------------------------------------------------------
------------- En esta parte es donde se desarrolla todo el programa ------------
--------------------------------------------------------------------------------
action = function(host)
-- Añadimos los encabezados de las columnas
  tab.addrow(output, "HOP", "RTT", "ADDRESS", "GEOLOCATION")
  -- Empezamos el conteo de los saltos
  for count = 1, #host.traceroute do
    local hop = host.traceroute[count]
    if hop.ip then
      local rtt = tonumber(hop.times.srtt) * 1000
      local geolocation
      if not ipOps.isPrivate(hop.ip) then
        -- Le pasamos como argumento la IP que estamos checando y
        -- con la biblioteca ip0ps compararemos la ip que tenemos con la del salto que daremos
        -- esto se realizará para no caer en una especie de ciclo.
        geolocation = geoLookup(hop.ip, ipOps.compare_ip(hop.ip, "eq", host.ip) )
      end
      output_hop(count, hop.ip, hop.name, rtt, geolocation)
    end
  end

  if (#output_structured > 0) then
    output = tab.dump(output)
    return output_structured, stdnse.format_output(true, output)
  end
end