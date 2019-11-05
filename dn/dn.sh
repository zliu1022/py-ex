# larger files: stackoverflow.com/a/32742700/4773609 
dn_large(){
    curl -c ./cookies "https://drive.google.com/uc?export=download&id=$1" > ./intermezzo.html
    curl -L -b ./cookies "https://drive.google.com$(cat ./intermezzo.html | grep -Po 'uc-download-link" [^>]* href="\K[^"]*' | sed 's/\&amp;/\&/g')" > $2
}

# small file: https://unix.stackexchange.com/questions/136371/how-to-download-a-folder-from-google-drive-using-terminal/148674
#wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=FILEID' -O $filename

id=1Hw5SpQXyGTQ73y-JnuR89KTWz-DhDeCP
filename=OZ05.gz
dn_large $id $filename

id=1Qw2xdibPiYksy5IG5x0ZagIXu1CVr-lM
filename=OZ06.gz
dn_large $id $filename

id=1064WHhoEO4D1yhLa-RMcreKOjhQ1OkZb
filename=OZ07.gz
dn_large $id $filename

id=1VWFJyAezhst5tTbWa2Z6N4HAxKjMaDVT
filename=OZ08.gz
dn_large $id $filename

id=1-9efNWQJyjObBxha7hKScGwjsM1fqN8x
filename=OZ09.gz
dn_large $id $filename

id=1uHlL3I8xbXW88eb8aJTbhxY51uRvlwoN
filename=OZ10.gz
dn_large $id $filename

id=1FVEY4HjA1MoqJbDpj2IB8Qu8Ad5awR7Z
filename=OZ11.gz
dn_large $id $filename

id=1Hsa9l-NErOmq1iBnSnIzszZwNferjDXs
filename=OZ12.gz
dn_large $id $filename

id=1tO0nAE-rIKmC5LcuGj3G2_GbyKFvPSD7
filename=OZ13.gz
dn_large $id $filename

id=16kBDduq9lg6YJBQfhDae62TC9G1CURh-
filename=OZ14.gz
dn_large $id $filename

id=1HNwr4e5yMVS06TqaYRpOQm7S5rtfJEhS
filename=OZ15.gz
dn_large $id $filename

id=18YSTOz90MuLvlphNeOBBWL3_jsjCEX52
filename=OZ16.gz
dn_large $id $filename

id=1DNss0FBWBCPM8pCOpCNvZOZK6-WNDc6a
filename=OZ17.gz
dn_large $id $filename

id=1dPXJsnwR2M_IIOGbjReUUQNELUXyBTT3
filename=OZ18.gz
dn_large $id $filename

