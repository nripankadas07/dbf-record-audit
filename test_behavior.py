import struct,unittest
from dbf_record_audit import analyze,example,MAX_BYTES
def changed(offset,data):
    value=bytearray(example());value[offset:offset+len(data)]=data;return bytes(value)
class Behavior(unittest.TestCase):
    def test_mixed_scale_sum_preserves_small_contribution(self):
        from decimal import localcontext
        head=bytearray(65);head[0]=3;struct.pack_into('<IHH',head,4,2,65,21)
        head[32:34]=b'N\0';head[43]=ord('N');head[48]=20;head[49]=18;head[64]=13
        raw=bytes(head)+b' '+b'99999999999999999999'+b' '+b'0.000000000000000001'
        with localcontext() as context:
            context.prec=6
            result=analyze(raw)
        self.assertEqual(result['groups']['active']['fields']['N']['sum'],'99999999999999999999.000000000000000001')
    def test_exact_decimal_and_deleted(self):
        r=analyze(example());self.assertEqual(r['finding_count'],0);self.assertEqual(r['groups']['active']['fields']['AMOUNT']['sum'],'0.30');self.assertEqual(r['groups']['deleted']['fields']['AMOUNT']['sum'],'9.99')
    def test_invalid_date(self):
        r=analyze(changed(129+1+8,b'20230229'));self.assertEqual(r['findings'][0]['reason'],'invalid calendar date')
    def test_logical(self):self.assertEqual(analyze(changed(129+17,b'X'))['finding_count'],1)
    def test_numeric_precision(self):self.assertEqual(analyze(changed(130,b'   0.123'))['finding_count'],1)
    def test_numeric_no_cleanup(self):
        for value in [b'    0,10',b'    ****',b'     1e2']:
            with self.subTest(value=value):self.assertEqual(analyze(changed(130,value))['finding_count'],1)
    def test_missing_values(self):
        r=analyze(changed(130,b' '*8+b'00000000'+b'?'));self.assertEqual(r['finding_count'],0);self.assertEqual(r['groups']['active']['fields']['WHEN']['missing'],1)
    def test_no_eof_marker_required(self):self.assertEqual(analyze(example()[:-1])['finding_count'],0)
    def test_extra_bytes_rejected(self):
        with self.assertRaises(ValueError):analyze(example()+b'x')
    def test_count_mismatch(self):
        with self.assertRaises(ValueError):analyze(changed(4,struct.pack('<I',4)))
    def test_record_width(self):
        with self.assertRaises(ValueError):analyze(changed(10,struct.pack('<H',19)))
    def test_descriptor_terminator(self):
        with self.assertRaises(ValueError):analyze(changed(128,b'\0'))
    def test_duplicate_name(self):
        with self.assertRaises(ValueError):analyze(changed(64,b'AMOUNT\0'))
    def test_unsupported_types(self):
        for value in [b'M',b'F',b'I']:
            with self.subTest(value=value),self.assertRaises(ValueError):analyze(changed(43,value))
    def test_memo_version(self):
        with self.assertRaises(ValueError):analyze(changed(0,b'\x83'))
    def test_bad_deletion_flag(self):
        with self.assertRaises(ValueError):analyze(changed(129,b'?'))
    def test_bad_width_decimals(self):
        for offset,value in [(48,b'\0'),(49,b'\x08'),(80,b'\x07'),(112,b'\x02')]:
            with self.subTest(offset=offset),self.assertRaises(ValueError):analyze(changed(offset,value))
    def test_byte_budget(self):
        with self.assertRaises(ValueError):analyze(b'\0'*(MAX_BYTES+1))
    def test_header_bounds(self):
        for length in [0,32,34,4097]:
            with self.subTest(length=length),self.assertRaises(ValueError):analyze(changed(8,struct.pack('<H',length)))
if __name__=='__main__':unittest.main()
