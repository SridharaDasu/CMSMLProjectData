#ifndef UCTRegion_hh
#define UCTRegion_hh

class UCTRegion {
public:
  UCTRegion(double et, int pos, bool ele, bool tau) {
    if (et <= 0) _bits = 0;
    else if (et < 1024.0) _bits = uint16_t(et); // 10-bit et
    else _bits = 0x3FF;
    _bits |= (pos << 10);
    if (ele) _bits |= 0x4000;
    if (tau) _bits |= 0x8000;
  }
  uint16_t bits() {return _bits;}
private:
  uint16_t _bits;
};

#endif
