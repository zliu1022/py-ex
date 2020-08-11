#安装
import time
import os
import random

print (time.asctime( time.localtime(time.time())))
!gdown --id 1ELLp8m-RDsAfX8VR-cZwfkTYWXaSRFz9
!unzip -o lz018_colab_0927.zip  >  /dev/null
!mkdir -p ~/.local/share/leela-zero
result = !/opt/bin/nvidia-smi 
if("K80" in result[7]):
  print("K80~~~~~~~~~~")
  !cp leelaz_opencl_tuning_K80_1441 ~/.local/share/leela-zero/leelaz_opencl_tuning
elif("T4" in result[7]):
  print("T4~~~~~~~~~~")
  !cp leelaz_opencl_tuning_T4_4735 ~/.local/share/leela-zero/leelaz_opencl_tuning
!mv *.so.* /usr/lib/x86_64-linux-gnu
!chmod a+x autogtp
!chmod a+x leelaz

#开始跑谱
print (time.asctime( time.localtime(time.time()) ))
!./autogtp    -k ./train/

