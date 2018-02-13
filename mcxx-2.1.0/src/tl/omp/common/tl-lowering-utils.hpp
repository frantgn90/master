/*--------------------------------------------------------------------
  (C) Copyright 2006-2015 Barcelona Supercomputing Center
                          Centro Nacional de Supercomputacion
  
  This file is part of Mercurium C/C++ source-to-source compiler.
  
  See AUTHORS file in the top level directory for information
  regarding developers and contributors.
  
  This library is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation; either
  version 3 of the License, or (at your option) any later version.
  
  Mercurium C/C++ source-to-source compiler is distributed in the hope
  that it will be useful, but WITHOUT ANY WARRANTY; without even the
  implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
  PURPOSE.  See the GNU Lesser General Public License for more
  details.
  
  You should have received a copy of the GNU Lesser General Public
  License along with Mercurium C/C++ source-to-source compiler; if
  not, write to the Free Software Foundation, Inc., 675 Mass Ave,
  Cambridge, MA 02139, USA.
--------------------------------------------------------------------*/



#ifndef TL_LOWERING_UTILS_HPP
#define TL_LOWERING_UTILS_HPP

#include "tl-nodecl.hpp"
#include "tl-datareference.hpp"
#include "tl-type.hpp"

namespace TL { namespace Lowering { namespace Utils {

    namespace Fortran
    {
        //FIXME: ADD DESCRIPTIONS!
        Nodecl::NodeclBase get_lower_bound(Nodecl::NodeclBase expr, int dimension_num);

        Nodecl::NodeclBase get_upper_bound(Nodecl::NodeclBase expr, int dimension_num);

        Nodecl::NodeclBase get_size_for_dimension(const TL::DataReference& data_ref, TL::Type array_type, int dimension_num);
    }


} } }

#endif // TL_LOWERING_UTILS
