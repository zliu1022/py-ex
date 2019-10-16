# no handicap
CMD=/Users/zliu/go/leela-zero/leelaz-dual
RESIGN=1
THREAD=4
GAMES=10

#weight 1
WEIGHT_1=/Users/zliu/go/weights/5x64/35.gz
PLAYOUT_1=1500

#weight 2
WEIGHT_2=/Users/zliu/go/weights/OZ/OZ14.gz
START_KOMI=80
KOMI_STEP=5
PLAYOUT_2=1200

:<<!
WEIGHT_2=/Users/zliu/go/weights/GX/GX5B.gz
START_KOMI=130
KOMI_STEP=6
PLAYOUT_2=3200

WEIGHT_2=/Users/zliu/go/weights/15x192/15b-238-136k.gz
START_KOMI=60
KOMI_STEP=5
PLAYOUT_2=3200
!

get_name_from_path(){
    tmp=`echo ${1#*weights/}`
    tmp=`echo ${tmp#*/}`
    name=`echo ${tmp%.gz*}`
    echo $name
    return $?
}
W_NAME1=`echo $(get_name_from_path $WEIGHT_1)`
W_NAME2=`echo $(get_name_from_path $WEIGHT_2)`

case $1 in
"normal")
    # normal game
    BLACK="$CMD -g --noponder --timemanage off -t$THREAD -r$RESIGN -w $WEIGHT_1 -p$PLAYOUT_1"
    WHITE="$CMD -g --noponder --timemanage off -t$THREAD -r$RESIGN -w $WEIGHT_2 -p$PLAYOUT_2"
    SGFNAME="$W_NAME1"-p"$PLAYOUT_1"_v_"$W_NAME2"-p"$PLAYOUT_2"-"$GAMES"
    PARA="-verbose -auto -games $GAMES -alternate -size 19 -komi 7.5 -sgffile $SGFNAME -time 7200m"
    ;;
"handicap")
    # handicap game
    #BLACK="$CMD -g --noponder --timemanage off -t$THREAD -r$RESIGN -w $WEIGHT_1 -p$PLAYOUT_1"
    BLACK="java -jar gogui-client.jar 192.168.1.136 8801"
    #WHITE="$CMD -g --noponder --timemanage off -t$THREAD -r$RESIGN -w $WEIGHT_2 -p$PLAYOUT_2 --komi $START_KOMI --kmrate 0.65 --kmstep $KOMI_STEP"
    WHITE="ssh -i /Users/zliu/outline zliu1022@35.223.182.248 /home/zliu1022/go/leelaz-dual -g --noponder --timemanage off -t$THREAD -r$RESIGN -w /home/zliu1022/go/OZ14.gz -p$PLAYOUT_2 --komi $START_KOMI --kmrate 0.65 --kmstep $KOMI_STEP"
    #SGFNAME="$W_NAME1"-p"$PLAYOUT_1"-h4_v_"$W_NAME2"-p"$PLAYOUT_2"-"$GAMES"
    SGFNAME=zen7-s1500-h4_v_"$W_NAME2"-p"$PLAYOUT_2"-"$GAMES"
    PARA="-openings /Users/zliu/github/Webgo/sgf/handicap/h4/ -verbose -auto -games $GAMES -size 19 -komi 0 -sgffile $SGFNAME -time 7200m"
    ;;
*)
    echo "para error"
    exit
    ;;
esac

:<<!
echo black "$BLACK"
echo white "$WHITE"
echo para $PARA
!

java -jar gogui-twogtp.jar -black "$BLACK" -white "$WHITE" $PARA
#./match.sh handicap >&1 | tee match-201909251550.log
