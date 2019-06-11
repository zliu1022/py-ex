import math
def main():
    print('40 Blocks\n')
    filename=input('Please enter the name of the current weight: ')
    w1 = open(filename, 'rt')
    filename=input('Please enter the name of the completed file: ')
    weight = open(filename, 'wt')
    print('Processing.')
    n = 0
    while n<336:
        v1 = [float(x) for x in w1.readline().split()]
        if n==0: weight.write('1')
        else:
            weight.write('\n')
            for i,x in enumerate(v1):
                weight.write('%.7g ' % (   x  ))
        n += 1 
    while n>335 and n<339:
        v1 = [float(x) for x in w1.readline().split()]
        if n==0: weight.write('1')
        else:
            weight.write('\n')
            for i,x in enumerate(v1):
                weight.write('%.7g ' % (    x*(1-((math.sqrt(x*x))**(1/8))/2)  ))
        n += 1 
    print('Finished.')
    weight.close()
if __name__ == '__main__': main()