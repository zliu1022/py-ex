# larger files: stackoverflow.com/a/32742700/4773609 
dn_large(){
    curl -c /tmp/cookies "https://drive.google.com/uc?export=download&id=$1" > /tmp/intermezzo.html
    echo $?
    curl -L -b /tmp/cookies "https://drive.google.com$(cat /tmp/intermezzo.html | grep -Po 'uc-download-link" [^>]* href="\K[^"]*' | sed 's/\&amp;/\&/g')" > $2
}

# small file: https://unix.stackexchange.com/questions/136371/how-to-download-a-folder-from-google-drive-using-terminal/148674
#wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=FILEID' -O $filename

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
