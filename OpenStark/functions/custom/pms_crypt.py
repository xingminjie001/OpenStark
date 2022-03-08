
import gzip,base64,codecs,re
from io import BytesIO

class PMSCrypt(object):
    def pms_encode(self,content):
        b = content.encode('utf-8')
        buf = BytesIO()
        f = gzip.GzipFile(mode='wb', fileobj=buf)
        try:
            f.write(b)
        finally:
            f.close()
        compress_data=buf.getvalue()
        compress_data=bytes.decode(base64.b64encode(compress_data))
        #compress_data=str(base64.b64encode(compress_data))
        print(type(compress_data),compress_data)
        return compress_data
    def pms_decode(self,content):
        compressed_data=base64.b64decode(content)
        compressed_stream = BytesIO(compressed_data)
        gzipper = gzip.GzipFile(fileobj=compressed_stream)
        uncompressed_data=codecs.getreader("utf-8")(gzipper)
        uncompressed_data = uncompressed_data.read()
        if '<?xml version="1.0"?>' in uncompressed_data:
            uncompressed_data=uncompressed_data.replace('<?xml version="1.0"?>','')
        return str(uncompressed_data)

    def uncompress_data(self,data):
       result = re.search(r'H4(.*?)<',str(data))
       try:
            raw_data = result.group().split('<')[0]
            new_data = self.PMS_decode(raw_data)
            un_data = re.sub(r'H4(.*?)<', new_data + '<', str(data))
            return un_data
       except:
           return data



if __name__ == '__main__':
    content = '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'

    compress_data1 = PMSCrypt().pms_decode(content)
    compress_data = PMSCrypt().pms_encode(compress_data1)





