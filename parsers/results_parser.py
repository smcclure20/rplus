# run starts with ===
# then record sender lines
import sys

def get_token_data(token):
    return token.split("=")[1].removesuffix(",").strip()

input_file = open(sys.argv[1], "r")
output_file = open(sys.argv[2], "w")
cfg_file = open(sys.argv[3], "w")

output_file.write("Config,Throughput,Delay\n")
cfg_file.write("ConfigNum,MeanOn,MeanOff,Nsrc,LinkPpt,Delay,BufferSize,Sloss\n")

cfg_num = 0
for line in input_file.readlines():
    if "===" in line:
        cfg_num += 1
    elif "config:" in line:
        tokens = line.split(" ")
        mean_on = get_token_data(tokens[1])
        mean_off = get_token_data(tokens[2])
        nsrc = get_token_data(tokens[3])
        link_ppt = get_token_data(tokens[4])
        delay = get_token_data(tokens[5])
        buffer_size = get_token_data(tokens[6])
        sloss = get_token_data(tokens[7])
        cfg_file.write("{},{},{},{},{},{},{},{}\n".format(cfg_num, mean_on, mean_off, nsrc, link_ppt, delay, buffer_size, sloss))
    elif "sender:" in line:
        tokens = line.split(" ")
        tput = tokens[1].removeprefix("tp=").removesuffix(",")
        delay = tokens[2].removeprefix("del=").strip()
        output_file.write("{},{},{}\n".format(cfg_num, tput, delay))

input_file.close()
output_file.close()
cfg_file.close()

