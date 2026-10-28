import ctypes, wave, array, sys
import espeakng_loader as e
lib = ctypes.CDLL(e.get_library_path())
CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_short), ctypes.c_int, ctypes.c_void_p)
buf = array.array('h')
@CB
def cb(wav, n, ev):
    if wav and n > 0: buf.extend(wav[:n])
    return 0
lib.espeak_Initialize.restype = ctypes.c_int
sr = lib.espeak_Initialize(2, 0, e.get_data_path().encode(), 0)
lib.espeak_SetSynthCallback(cb)
def synth(text, path, voice=b"es+f3", rate=150, pitch=55):
    global buf
    buf = array.array('h')
    lib.espeak_SetVoiceByName(voice)
    lib.espeak_SetParameter(1, rate, 0); lib.espeak_SetParameter(3, pitch, 0)
    b = text.encode()
    lib.espeak_Synth(b, len(b) + 1, 0, 0, 0, 0x1 | 0x1000, None, None)  # chars UTF8 flag 1
    lib.espeak_Synchronize()
    w = wave.open(path, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(buf.tobytes()); w.close()
    return len(buf) / sr
if __name__ == "__main__":
    print(synth("Imagina que tienes ochenta y seis mil cuatrocientos dólares en el banco.", "test.wav"))
