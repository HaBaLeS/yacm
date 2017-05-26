#filters output
import subprocess
proc = subprocess.Popen(['-i wlp3s0', '-nn', '-t' ,'-l', 'tcp and not ip6'],1,'tcpdump',stdout=subprocess.PIPE,stdin = subprocess.PIPE,
    universal_newlines = True)
while True:
  line = proc.stdout.readline()
  if line != '':
    #the real code does filtering here
    data = str(line).split(' ')
    src = data[1]
    dst = data[3][:-1] # remove last ':'

    dst_ip = ''
    for block in dst.split('.')[:-1]:
        dst_ip = dst_ip + '.' +block
    dst_ip = dst_ip[1:]

    src_ip = ''
    for block in src.split('.')[:-1]:
        src_ip = src_ip + '.' + block
    src_ip = src_ip[1:]

    print("%s -> %s"%(src_ip,dst_ip))
  else:
    break

