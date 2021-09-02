#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#  This file is part of the `pypath` python module
#
#  Copyright
#  2014-2021
#  EMBL, EMBL-EBI, Uniklinik RWTH Aachen, Heidelberg University
#
#  File author(s): Dénes Türei (turei.denes@gmail.com)
#                  Nicolàs Palacio
#                  Olga Ivanova
#
#  Distributed under the GPLv3 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#  Website: http://pypath.omnipathdb.org/
#

import collections

import bs4

import pypath.resources.urls as urls
import pypath.share.curl as curl
import pypath.share.common as common
import pypath.share.session as session

_logger = session.Logger(name = 'unichem_input')
_log = _logger._log


def unichem_sources():
    """
    List of ID types in UniChem.

    Returns:
        (dict): A dict with ID type numeric IDs as keys and ID type labels
            as values.
    """

    url = urls.urls['unichem']['sources']
    c = curl.Curl(url, large = False, silent = False)
    soup = bs4.BeautifulSoup(c.result, 'html.parser')
    result = {}

    for table in soup.find_all('table'):

        if table.find('tr').text.strip().startswith('src_id'):

            for row in table.find_all('tr')[2:]:

                fields = row.find_all('td')

                result[fields[0].text] = fields[1].text.strip()

    return result


def unichem_mapping(id_type, target_id_type):
    """
    Identifier translation data from UniChem.

    Args:
        id_type (int,str): An ID type in UniChem: either the integer ID or
            the string label of a resource. For a full list see
            `unichem_sources`.
        target_id_type (int,str): An ID type in UniChem, same way as
            `id_type`.

    Returns:
        (dict): A dictionary with ID translation data, keys are IDs of
            `id_type`, values are sets of IDs of `target_id_type`.
    """

    src_to_label = unichem_sources()
    label_to_src = common.swap_dict(src_to_label)

    def get_src_id(id_type):

        id_type = str(id_type)
        _id_type = label_to_src.get(id_type, id_type)

        if not _id_type.isdigit() or _id_type not in src_to_label:

            msg = 'No such ID type: `%s`.' % id_type
            _log(msg)
            raise ValueError(msg)

        return _id_type


    id_type = get_src_id(id_type)
    target_id_type = get_src_id(target_id_type)

    url = urls.urls['unichem']['mapping'] % (id_type, id_type, target_id_type)
    c = curl.Curl(url, large = True, silent = False)
    result = collections.defaultdict(set)
    _ = next(c.result)

    for r in c.result:

        src_id, tgt_id = r.strip().split('\t')
        result[src_id].add(tgt_id)

    return dict(result)