from obspy import UTCDateTime
import dataset as dataset
from obspy import Stream
import obspy

class Picks:
    def __init__(self, phase, time, travel_residual="", fpos = 0, fneg = 0) :
        self.phase = phase
        self.time = time
        self.travel_residual = travel_residual
        self.falsePos = fpos
        self.falseNeg = fneg
class Event:
    def __init__(self, evtID, oriTime, station, wavefile):
        self.evtID = evtID
        self.oriTime = oriTime
        self.station = station
        self.wavefileName = wavefile
        self.manPick_S = {}
        self.manPick_P = {}
        self.autoPick_S = {}
        self.autoPick_P = {}

# Main
base_path = "./Data/"
metadata_ori_path = base_path + "metadataTodas_B.csv"
waveforms_path = base_path + "Waveforms_SEI"
catalog = {}
stations = {'PFAV', 'PVNV', 'PRIB', 'PBIS', 'PT01', 'PPAD', 'ASBA', 'PRAM'}
oldID = ""
datset = [ "ethz", "geofon", "instance", "stead"]
di =2

model = sbm.PhaseNetLight.load("./Best/PNL_Fogo3")
print(datset[di])
#---------------------------------------------------------------------------------------------------------
#------------------------------ Carregar Dados -----------------------------------------------------------
#---------------------------------------------------------------------------------------------------------
print("--- Read events")


#---------------------------------------------------------------------------------------------------------
#------------------------------ Aplicar Modelo -----------------------------------------------------------
#---------------------------------------------------------------------------------------------------------
