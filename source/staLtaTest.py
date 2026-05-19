from obspy import UTCDateTime
import csv
#import seisbench.models as sbm
#from obspy import Stream
#import obspy
#import seisbench
from urllib.parse import urljoin
from staLta import STALTAPhasePicker

#seisbench.remote_root = "https://hifis-storage.desy.de/Helmholtz/HelmholtzAI/SeisBench/"
#seisbench.remote_data_root = urljoin(seisbench.remote_root, "datasets/")
#seisbench.remote_model_root = urljoin(seisbench.remote_root, "models/v3/")

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
di =1
#model = sbm.BasicPhaseAE.from_pretrained(datset[di])
#model = sbm.BasicPhaseAE.load("./Best/BP_Fogo3")
#model = sbm.EQTransformer.from_pretrained(datset[di])
#model = sbm.EQTransformer.load("./Best/terTodas_Noise5")
#model = sbm.EQTransformer.load("./Best/EQ_Fogo4")
#model = sbm.GPD.from_pretrained(datset[di])
#model = sbm.PhaseNet.from_pretrained(datset[di])
#model = sbm.PhaseNet.load("./Best/terTodas_Fogo_PN")
#model = sbm.PhaseNet.load("./Best/PN_Fogo3")
#model = sbm.PhaseNet.load("./Best/terTodas_Fogo")
#model = sbm.PhaseNetLight.from_pretrained(datset[di])
#model = sbm.PhaseNetLight.load("./Best/PNL_Fogo3")
#th = 0.7
#model.default_args = {"P_threshold": th, "S_threshold": th}
#model.cuda()
print(datset[di])
#---------------------------------------------------------------------------------------------------------
#------------------------------ Carregar Dados -----------------------------------------------------------
#---------------------------------------------------------------------------------------------------------
print("--- Read events")
cnt = 0
with open(metadata_ori_path, newline='\n') as csvfile:
    md_ori = csv.DictReader(csvfile)
    evt = ""
    for row in md_ori:
        if (oldID != row["source_id"]):
            if evt != "":
                catalog[oldID] = evt
            oldID = row["source_id"]
            evt = Event(row["source_id"], row["source_origin_time"], row["station_code"],row["filename"])
            #cnt = cnt + 1
            #if cnt == 100: break
        if row["station_code"] not in stations: 
            continue
        evt.manPick_P[row["station_code"]] = Picks("P", row["path_p_travel_s"], row["path_p_residual_s"])
        evt.autoPick_P[row["station_code"]] = Picks("P", "", "")
        evt.manPick_S[row["station_code"]] = Picks("S", row["path_s_travel_s"], row["path_s_residual_s"])        
        evt.autoPick_S[row["station_code"]] = Picks("S", "", "")        
catalog[evt.evtID] = evt

#---------------------------------------------------------------------------------------------------------
#------------------------------ Aplicar Modelo -----------------------------------------------------------
#---------------------------------------------------------------------------------------------------------
print("--- Autopicks")

#model.cuda()

evt = ""
falseP = 0
falseS = 0
ln = len(catalog)
cnt = 0
picker = STALTAPhasePicker(
        sta_seconds=1.0,
        lta_seconds=10.0,
        trigger_on=3.5,
        trigger_off=1.0,
    )

for evt in catalog:
    cnt = cnt + 1
    t_dif = 0.5
    print("--- " + str(cnt) + " of " + str(ln), end="\r")
    #stream = obspy.read("./Data/Waveforms_SEI/" + catalog[evt].wavefileName)
    picks = picker.pick("./Data/Waveforms_SEI/" + catalog[evt].wavefileName)
    #outputs = model.classify(stream)
    for i in range(len(picks)):
        if picks[i]['phase'] == "P":
            staCode = picks[i]['station']
            if staCode in catalog[evt].autoPick_P:
                if catalog[evt].manPick_P[staCode].time != "":
                    newt = UTCDateTime(picks[i]['time']) - UTCDateTime(catalog[evt].manPick_P[staCode].time)
                    if catalog[evt].autoPick_P[staCode].time == "" and abs(newt) < t_dif:
                        catalog[evt].autoPick_P[staCode] = Picks(phase="P", time=picks[i]['time'],fpos=0)
                    else:
                        catalog[evt].autoPick_P[staCode].falsePos = catalog[evt].autoPick_P[staCode].falsePos + 1
                        falseP = falseP + 1
                        if catalog[evt].autoPick_P[staCode].time != "":
                            oldt = UTCDateTime(catalog[evt].autoPick_P[staCode].time) - UTCDateTime(catalog[evt].manPick_P[staCode].time)
                            if abs(newt) < abs(oldt):
                                catalog[evt].autoPick_P[staCode].time = time=picks[i]['time']
                else:
                    catalog[evt].autoPick_P[staCode].falsePos = catalog[evt].autoPick_P[staCode].falsePos + 1
                    catalog[evt].autoPick_P[staCode].time = time=picks[i]['time']

        if picks[i]['phase'] == "S":
            staCode = picks[i]['station']
            if staCode in catalog[evt].autoPick_S:
                if catalog[evt].manPick_S[staCode].time != "":
                    newt = UTCDateTime(picks[i]['time']) - UTCDateTime(catalog[evt].manPick_S[staCode].time)
                    if catalog[evt].autoPick_S[staCode].time == "" and abs(newt) < t_dif:
                        catalog[evt].autoPick_S[staCode] = Picks(phase="S", time=picks[i]['time'],fpos=0)
                    else:
                        catalog[evt].autoPick_S[staCode].falsePos = catalog[evt].autoPick_S[staCode].falsePos + 1
                        falseS = falseS + 1
                        if catalog[evt].autoPick_S[staCode].time != "":
                            oldt = UTCDateTime(catalog[evt].autoPick_S[staCode].time) - UTCDateTime(catalog[evt].manPick_S[staCode].time)
                            if abs(newt) < abs(oldt):
                                catalog[evt].autoPick_S[staCode].time = picks[i]['time']
                else:
                        catalog[evt].autoPick_S[staCode].falsePos = catalog[evt].autoPick_S[staCode].falsePos + 1
                        catalog[evt].autoPick_S[staCode].time = picks[i]['time']


print("")

#---------------------------------------------------------------------------------------------------------
#------------------------------ Guardar CSV --------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------
print("--- Write to CSV")
with open("./Compara/Todas_B/compare2.csv", "w", newline="\n") as csvfile:
    fieldnames =["source_id", "source_origin_time", "station_code", "path_p_travel_man", "path_p_travel_auto", "path_p_diff", "false_pos_P", "path_s_travel_man", "path_s_travel_auto", "path_s_diff", "false_pos_S"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=",")
    writer.writeheader()
    row = {}
    for evtid in catalog:
        evt = catalog[evtid]
        for picks in evt.manPick_P:
            row["source_id"] = evt.evtID
            row["source_origin_time"] = evt.oriTime
            row["station_code"] = picks
            row["path_p_travel_man"] = evt.manPick_P[picks].time
            row["path_s_travel_man"] = evt.manPick_S[picks].time
            row["path_p_travel_auto"] = evt.autoPick_P[picks].time
            row["path_s_travel_auto"] = evt.autoPick_S[picks].time
            row["false_pos_P"] =  evt.autoPick_P[picks].falsePos
            row["false_pos_S"] =  evt.autoPick_S[picks].falsePos

            if (evt.manPick_P[picks].time != "" and evt.autoPick_P[picks].time != ""):
                row["path_p_diff"] = UTCDateTime(evt.autoPick_P[picks].time) - UTCDateTime(evt.manPick_P[picks].time)
            else:
                row["path_p_diff"] = ""

            if (evt.manPick_S[picks].time != "" and evt.autoPick_S[picks].time != ""):
                row["path_s_diff"] = UTCDateTime(evt.autoPick_S[picks].time) - UTCDateTime(evt.manPick_S[picks].time)
            else:
                row["path_s_diff"] = ""
            writer.writerow(row)
          
print("--- Done")
print(" False P " + str(falseP))
print(" False S " + str(falseS))