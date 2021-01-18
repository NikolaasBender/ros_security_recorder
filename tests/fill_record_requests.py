import src.rtsp_manager as manager
import src.rtsp_recorder as recorder

def selectTest():
    repeat = recorder.createStartSelect(True)
    one_off = recorder.createStartSelect(False)

    if  repeat == '' and one_off == '':
        return True
    return False




def tester():
    selects = selectTest()
    print('select test return:', selects)



tester()