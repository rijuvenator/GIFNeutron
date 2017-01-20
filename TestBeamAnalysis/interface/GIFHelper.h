#ifndef GIFHELPER_H
#define GIFHELPER_H

#include <limits>
#include <iostream>
#include "DataFormats/MuonDetId/interface/CSCDetId.h"

namespace GIFHelper
{
	//Conversion function to check validity
	template<typename Target, typename Source>
	Target convertTo(Source source, const char name[], bool lenient = false, bool* good = 0)
	{
		Target converted = static_cast<Target>(source);

		if (static_cast<Source>(converted) != source) {
			const Target lowest	= !std::numeric_limits<Target>::is_signed
				? 0
				: std::numeric_limits<Target>::has_infinity
				? -std::numeric_limits<Target>::infinity()
				:  std::numeric_limits<Target>::min()
				;

			std::string problem = "convertTo(): Source value " + std::to_string((double)	source) + " outside of target range "
				+"["+std::to_string((double)  lowest)+","+std::to_string((double)	std::numeric_limits<Target>::max())+"]"
				+ " for '" + name +"'";

			if (good) *good	= false;
			if (lenient)
			{
				std::cerr << "WARNING: " << problem << std::endl;
				return	( source > static_cast<Source>(std::numeric_limits<Target>::max())
					? std::numeric_limits<Target>::max()
					: lowest
				);
			}
			throw std::range_error( problem);
		}

		return converted;
	}


	unsigned short int chamberSerial( CSCDetId id );
}

#endif
