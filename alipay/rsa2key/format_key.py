#-*-coding:utf-8 -*-

def get_pubkey():
    """
    """
    with open("pubkey.txt","r") as f:
        pubkey = f.read()
        print len(pubkey),2222222222222222
        ind_list = filter(lambda x:x%64==0,[i for i in range(0,len(pubkey))])
        ind_range = [[x,x+64] if x+64<len(pubkey) else [x,-1] for x in ind_list]
        print pubkey
        print ind_list
        print ind_range
        str_range = [pubkey[x:x+64] if x+64<len(pubkey) else pubkey[x:] for x in ind_list]
        print str_range
        format_str = "\n".join(str_range)
        format_str = "-----BEGIN PUBLIC KEY-----\n"+format_str+"\n-----END PUBLIC KEY-----"
        print format_str


def get_privkey():
    """
    """
    with open("privkey.txt","r") as f:
        pubkey = f.read()
        print len(pubkey),2222222222222222
        ind_list = filter(lambda x:x%64==0,[i for i in range(0,len(pubkey))])
        ind_range = [[x,x+64] if x+64<len(pubkey) else [x,-1] for x in ind_list]
        print pubkey
        print ind_list
        print ind_range
        str_range = [pubkey[x:x+64] if x+64<len(pubkey) else pubkey[x:] for x in ind_list]
        print str_range
        format_str = "\n".join(str_range)
        format_str = "-----BEGIN RSA PRIVATE KEY-----\n"+format_str+"\n-----END RSA PRIVATE KEY-----"
        print format_str


if __name__ == "__main__":
    get_pubkey()
    #get_privkey()
