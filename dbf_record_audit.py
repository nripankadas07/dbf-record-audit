"""Read-only dBASE III plain-table structure and cell representation evidence."""
from __future__ import annotations
import argparse,datetime,hashlib,json,re,struct,sys
from decimal import Decimal,localcontext
from pathlib import Path
MAX_BYTES=4*1024*1024
def exact_add(left,right):
    # At most20 input digits,18 fractional places and20000 records:
    # at most25 integer+18 fractional digits. Do not inherit caller precision.
    with localcontext() as context:
        context.prec=64
        return left+right
def example():
    fields=[('AMOUNT','N',8,2),('WHEN','D',8,0),('OK','L',1,0)]
    records=[b' '+b'    0.10'+b'20240229'+b'Y',b' '+b'    0.20'+b'20240301'+b'T',b'*'+b'    9.99'+b'20240101'+b'N']
    head=bytearray(32);head[0]=3;head[1:4]=bytes([124,3,1]);struct.pack_into('<IHH',head,4,len(records),33+32*len(fields),18)
    for name,kind,width,decimals in fields:
        descriptor=bytearray(32);descriptor[:len(name)]=name.encode();descriptor[11]=ord(kind);descriptor[16:18]=bytes([width,decimals]);head.extend(descriptor)
    return bytes(head)+b'\r'+b''.join(records)+b'\x1a'
def analyze(raw):
    if len(raw)>MAX_BYTES or len(raw)<33 or raw[0]!=3:raise ValueError('plain dBASE III version03, at most4MiB required; no memo/VFP')
    count,header_len,record_len=struct.unpack_from('<IHH',raw,4)
    if count>20000 or header_len<65 or (header_len-33)%32 or header_len>len(raw):raise ValueError('invalid field header or record budget')
    nfields=(header_len-33)//32
    if not 1<=nfields<=128 or raw[header_len-1]!=13:raise ValueError('one to128 fields and exact descriptor terminator required')
    fields=[];names=set()
    for offset in range(32,header_len-1,32):
        d=raw[offset:offset+32];name_bytes=d[:11]
        if b'\0' not in name_bytes:raise ValueError('field name must terminate within11 bytes')
        name_bytes=name_bytes.split(b'\0',1)[0]
        try:name=name_bytes.decode('ascii')
        except UnicodeDecodeError:raise ValueError('ASCII field names required') from None
        if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]{0,9}',name) or name.casefold() in names:raise ValueError('unique ASCII identifier field names required')
        names.add(name.casefold());kind=chr(d[11]);width,decimals=d[16:18]
        if kind not in 'CNDL':raise ValueError('only C,N,D,L fields supported')
        if (kind=='C' and (not 1<=width<=254 or decimals)) or (kind=='N' and (not 1<=width<=20 or decimals>max(0,width-2))) or (kind=='D' and (width!=8 or decimals)) or (kind=='L' and (width!=1 or decimals)):raise ValueError('invalid field width or decimals')
        fields.append({'name':name,'type':kind,'width':width,'decimals':decimals})
    if record_len!=1+sum(f['width'] for f in fields):raise ValueError('record width differs from field widths')
    expected=header_len+count*record_len
    if len(raw)!=expected and not (len(raw)==expected+1 and raw[-1]==26):raise ValueError('record count/length mismatch or unexpected trailing bytes')
    groups={key:{'records':0,'fields':{f['name']:{'present':0,'missing':0,'invalid':0,**({'sum':'0','minimum':None,'maximum':None} if f['type']=='N' else {})} for f in fields}} for key in ('active','deleted')}
    issues=[];total=0
    def issue(index,field,deleted,reason):
        nonlocal total
        total+=1
        if len(issues)<512:issues.append({'record':index,'field':field,'deleted':deleted,'reason':reason})
    for index in range(count):
        offset=header_len+index*record_len;flag=raw[offset];offset+=1
        if flag not in (32,42):raise ValueError('invalid deletion flag at record'+str(index+1))
        deleted=flag==42;group=groups['deleted' if deleted else 'active'];group['records']+=1
        for f in fields:
            cell=raw[offset:offset+f['width']];offset+=f['width'];stats=group['fields'][f['name']];kind=f['type'];value=cell.strip(b' ');reason=None;missing=not value
            if kind=='N' and not missing:
                if not re.fullmatch(rb'[+-]?[0-9]+(?:\.[0-9]+)?',value):reason='invalid numeric representation'
                elif len(value.split(b'.',1)[1])>f['decimals'] if b'.' in value else False:reason='fraction exceeds declared decimals'
                if reason is None:
                    number=Decimal(value.decode('ascii'));stats['sum']=str(exact_add(Decimal(stats['sum']),number))
                    for key,choose in [('minimum',min),('maximum',max)]:stats[key]=str(number if stats[key] is None else choose(Decimal(stats[key]),number))
            elif kind=='D':
                missing=missing or value==b'00000000'
                if not missing:
                    if not re.fullmatch(rb'[0-9]{8}',cell):reason='invalid date representation'
                    else:
                        try:datetime.date(int(cell[:4]),int(cell[4:6]),int(cell[6:8]))
                        except ValueError:reason='invalid calendar date'
            elif kind=='L':
                missing=cell in (b' ',b'?')
                if not missing and cell not in (b'Y',b'y',b'T',b't',b'N',b'n',b'F',b'f'):reason='invalid logical representation'
            elif kind=='C' and any(byte<32 or byte==127 for byte in cell):reason='control byte in character field'
            if reason:stats['invalid']+=1;issue(index+1,f['name'],deleted,reason)
            elif missing:stats['missing']+=1
            else:stats['present']+=1
    return {'schema':'dbf-record-audit/v1','source_sha256':hashlib.sha256(raw).hexdigest(),'version':3,'language_driver_byte':raw[29],'header_bytes':header_len,'record_bytes':record_len,'fields':fields,'groups':groups,'finding_count':total,'findings':issues,'omitted_findings':total-len(issues),'scope':'plain dBASE III C/N/D/L; raw character bytes, no charset guessing, memo, conversion or business interpretation'}
def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('input',nargs='?');parser.add_argument('--make-example',metavar='NEW_FILE');args=parser.parse_args(argv)
    try:
        if args.make_example:
            if args.input:raise ValueError('choose input or example generation')
            with open(args.make_example,'xb') as stream:stream.write(example())
            return 0
        if not args.input:raise ValueError('input file required')
        with open(args.input,'rb') as stream:raw=stream.read(MAX_BYTES+1)
        result=analyze(raw);print(json.dumps(result,sort_keys=True,indent=2));return int(bool(result['finding_count']))
    except (ValueError,OSError) as error:print(str(error),file=sys.stderr);return 2
if __name__=='__main__':sys.exit(main())
