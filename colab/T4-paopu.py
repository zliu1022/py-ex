#T4
result = !/opt/bin/nvidia-smi
if("K80" in result[7]):
  print("GPU K80")
elif("T4" in result[7]):
  print("GPU T4")
  !rm -rf /content/run_lz_in_gg
  !git clone https://github.com/liujn2018/run_lz_in_gg.git
  !/usr/bin/python3 /content/run_lz_in_gg/paopu3.py
else:
  print("GPU")
