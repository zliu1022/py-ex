!git clone https://github.com/startnoob/sai_in_gg.git
!apt install qt5-default qt5-qmake curl > /dev/null
!apt install libboost-dev libboost-program-options-dev libopenblas-dev opencl-headers ocl-icd-opencl-dev > /dev/null
!apt update > /dev/null
!apt -qq install --no-install-recommends nvidia-opencl-icd-384 > /dev/null
!wget http://launchpadlibrarian.net/352962266/nvidia-opencl-icd-384_384.111-0ubuntu0.17.10.1_amd64.deb > /dev/null
!apt install -f ./nvidia-opencl-icd-384_384.111-0ubuntu0.17.10.1_amd64.deb > /dev/null
!apt -qq install --no-install-recommends nvidia-opencl-dev > /dev/null
!apt --fix-broken install > /dev/null
!cd sai_in_gg && ./autogtp --url http://sai.unich.it/ --username [Your_Name] --password [Your_Password] | grep minute
