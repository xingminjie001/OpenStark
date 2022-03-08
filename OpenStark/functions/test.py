from urllib.parse import unquote_plus
# 解析URL
def url_query_decode(query=''):
    query_dict = dict()
    print(query_dict)
    print(query)
    for line in unquote_plus(query).split('&'):
        line = line.split(sep='=', maxsplit=1)
        if len(line) == 2:
            query_dict[line[0]] = line[1]
            print(query_dict[line[0]])
    if len(query_dict) == len(query.split('&')):
        print('1', query_dict)
        return query_dict
    else:
        print('2',query)
        return query

str='<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><GetAccountDs_V1 xmlns="http://tempuri.org/"><buffers>H4sIAAAAAAAEAO29B2AcSZYlJi9tynt/SvVK1+B0oQiAYBMk2JBAEOzBiM3mkuwdaUcjKasqgcplVmVdZhZAzO2dvPfee++999577733ujudTif33/8/XGZkAWz2zkrayZ4hgKrIHz9+fB8/In7xRy/LbHn29KNHH300+uhZXS1eVVcv1otJXn/0aGf00ZvK+3t3hz55XdXt67Yulhfyzkm1nBVtUS1f/8Rz+mR3Z3+0+/DT0cH90d69/dHezsFo98HeaHfvYPRgh765Rx9/Otr99P5o92BnRI32D9B2d293BPB4dXdvX/6P93b3R/v068690e59+nmfmtD79wnqwf7o/qejB/ShwNzbezDa28WfBHVvZwRI9L8dAvIpvf2AOrlHrxFSQIJQA7yDh6M9arRPn+DnLiHzYLT/YPTw4ejgYPTpgSJDXxN+96jznREhvLf7kF4lgA/p//QRvbNLH+/uPhhRm/1dHtvu3n1peO/BiEA/eDgiLHap5/3RPfp0n1oAeeBHmO8yGjv8Bo1jH29Qc/ryPsA9YCR29/doqKDSg9EBffUArYAOoY2B744+3ccXGOfOLhP/Po+O5un421WblyczmqOTlyevd3Yx30Vezp4XTfvRo+/9YvnrRbbIqUk2nba//3K9MI1+MivX+nm1XrZj+/0vGYUvLqvff1URwIH3zNfd16Z1U+fN5e9/Xl4Mveo36b6+yq4X+bL9/dtV9+2tadbk6dU8X6br1Sqvtww498qd9LOPX778OG3R6OP/+i/5w/6zv/fP+jjNS3rv4//yT/ib5K/l7E6aNanXUReHevH7TxfL3sjrRdOum7H5NvJW1m54CV/23skXxXIWo9VWk5f5tE3doHmwW9+6c7Qj49uVge1gRGl6TgKfNqtpsTyv0vS7Z2++nW4tq7Kavr2T4v06x7e/f3u9Sj9LP77/cZrRW2bu6aMuOzCNPPR681Tn5wR0Oc2/Mewv5g5odwgygos5Y1ssU9OBfsLv6xCAeDvJ0quinXcB0Od2hLFBC2eEQ+uPvJjm03m2vIgO3XJlZZlcgIZvdaFmdf37z3rcs5WeHL8+/X3b73779IXDlptiGncf7uxs727vfpy+QYMXXz1/np4+f33aafr7tqcvnv6+7Z30+HWq/XS7n63a23YvTTd1//u2YVvuP+XutZ9u98283qSjzNcRkdvwln7b1zB1u8w39uc36b4Ojuu9OCfNW9XXY/ky9kq/M/+dSD/Mk9AdGxU3N4i+OsnKjW/i+77Kb4lLhzU+fxuZBNIqGyYB3/Zean//bDFoW/Tb7ktv8+tNEme+jhmyeqMdq/t9vazzi02d2e/7Kp2EfhNXmu+7L35er8imb2IsCJC06r6bvyM6b8DWft998ZhY4XWEybYg+KF+BKv9vvXvu/x9SZ7TD3hYmXz8e4rSMAA/DCRM/X/1N/wl//kf9Rf913/2X/bxN4fkt342kPwT/4z/4u/4o75BJH/XbxTJ//zv/Fv+y7/3T/0G0fuF3yh6/9nf/+f953/PX/gNorfzjaL3X/x5f81//kf9Td8gempbvyH0hAO/QfT2v1H0/vM/76/6z/+eP/MbRO/+N4veNy0an36z6P09f9p/8af9Hd8gep9/s+j9uX/Jf/1nfZOS+/obRe+//Hv/wv/qb/iL/6u/7a/4L/6ov/MbRPLsG0XyP/8j/vD/+g/9q/7zv+tP+maR/OqbRfIf+MNJTL5BJBG8MJgbW254OPqw3s4v+f4v+X8AfCcSbDATAAA=</buffers></GetAccountDs_V1></soap:Body></soap:Envelope>'
f=url_query_decode(str)