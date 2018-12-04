# MIT License
#
# Copyright (c) 2018 Omidiora Samuel, samparsky@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pytest

from bitcoinetl.jobs.export_blocks_job import ExportBlocksJob
from bitcoinetl.jobs.exporters.blocks_and_transactions_item_exporter import blocks_and_transactions_item_exporter
from tests.bitcoinetl.job.helpers import get_provider
from blockchainetl.thread_local_proxy import ThreadLocalProxy

import tests.resources
from tests.helpers import compare_lines_ignore_order, read_file, skip_if_slow_tests_disabled


RESOURCE_GROUP = 'test_export_blocks_job'

def read_resource(resource_group, file_name):
    return tests.resources.read_resource([RESOURCE_GROUP, resource_group], file_name)

@pytest.mark.parametrize("start_block, end_block, batch_size, resource_group, export_transactions ,provider_type,", [
    (50000, 50002, 2, 'block_without_transactions', False,'mock'),
    (50000, 50002, 2, 'block_with_transactions', True ,'mock'),
    skip_if_slow_tests_disabled([50000, 50002, 2, 'block_without_transactions', False, 'online']),
    skip_if_slow_tests_disabled([50000, 50002, 2, 'block_with_transactions', True, 'online']),
])
def test_export_blocks_job(tmpdir, start_block, end_block, batch_size, resource_group, export_transactions,provider_type):
    blocks_output_file = str(tmpdir.join('actual_block.json'))
    transactions_output_file = str(tmpdir.join("actual_transactions.json"))

    job = ExportBlocksJob(
        start_block=start_block,
        end_block=end_block,
        batch_size=batch_size,
        batch_rpc_provider=ThreadLocalProxy(lambda: get_provider(provider_type, lambda file: read_resource(resource_group, file))),
        max_workers=5,
        item_exporter=blocks_and_transactions_item_exporter(blocks_output_file, transactions_output_file),
        export_blocks=blocks_output_file is not None,
        export_transactions=export_transactions)
    job.run()

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_blocks.json'), read_file(blocks_output_file), provider_type == "online"
    )

    compare_lines_ignore_order(
        read_resource(resource_group, 'expected_transactions.json'), read_file(transactions_output_file), provider_type == "online"
    )