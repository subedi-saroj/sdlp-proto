import lux4600 as lux

proj = lux.projector.Projector(lux.IP, lux.DATA_PORT, lux.IMAGE_DATA_PORT, timeout=5) # default timeout set to ten

proj.check_connection()