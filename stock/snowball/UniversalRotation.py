import requests
import browser_cookie3
import pysnowball

def main():
    cj = browser_cookie3.load()
    for item in cj:
        if item.name == "xq_a_token" :
            print('%s = %s' % (item.name, item.value))
            strxq_a_token = 'xq_a_token=' + item.value + ';'
            pysnowball.set_token(strxq_a_token)

    print(pysnowball.quote_detail("SH501095"))

if __name__ == "__main__":
    main()