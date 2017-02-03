#include "Gif/NeutronSim/interface/GIFHelper.h"

unsigned short int GIFHelper::chamberSerial( CSCDetId id )
{
	int st = id.station();
	int ri = id.ring();
	int ch = id.chamber();
	int ec = id.endcap();
	int kSerial = ch;
	if (st == 1 && ri == 1) kSerial = ch;
	if (st == 1 && ri == 2) kSerial = ch + 36;
	if (st == 1 && ri == 3) kSerial = ch + 72;
	if (st == 1 && ri == 4) kSerial = ch;
	if (st == 2 && ri == 1) kSerial = ch + 108;
	if (st == 2 && ri == 2) kSerial = ch + 126;
	if (st == 3 && ri == 1) kSerial = ch + 162;
	if (st == 3 && ri == 2) kSerial = ch + 180;
	if (st == 4 && ri == 1) kSerial = ch + 216;
	if (st == 4 && ri == 2) kSerial = ch + 234;  // one day...
	if (ec == 2) kSerial = kSerial + 300;
	return convertTo<unsigned short int>(kSerial,"chamberSerial");
}
