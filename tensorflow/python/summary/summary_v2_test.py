# Copyright 2021 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests for the API surface of the V1 tf.summary ops when TF2 is enabled.

V1 summary ops will invoke V2 TensorBoard summary ops in eager mode.
"""

from tensorboard.summary import v2 as summary_v2
from tensorflow.python.framework import constant_op
from tensorflow.python.framework import dtypes
from tensorflow.python.framework import ops
from tensorflow.python.framework import test_util
from tensorflow.python.ops import summary_ops_v2
from tensorflow.python.platform import test
from tensorflow.python.summary import summary as summary_lib
from tensorflow.python.training import training_util


class SummaryV2Test(test.TestCase):

  @test_util.run_v2_only
  def test_scalar_summary_v2__w_writer(self):
    """Tests scalar v2 invocation with a v2 writer."""
    with test.mock.patch.object(
        summary_v2, 'scalar', autospec=True) as mock_scalar_v2:
      with summary_ops_v2.create_summary_file_writer('/tmp/test').as_default(
          step=1):
        i = constant_op.constant(2.5)
        tensor = summary_lib.scalar('float', i)
    # Returns empty string.
    self.assertEqual(tensor.numpy(), b'')
    self.assertEqual(tensor.dtype, dtypes.string)
    mock_scalar_v2.assert_called_once_with('float', data=i, step=1)

  @test_util.run_v2_only
  def test_scalar_summary_v2__wo_writer(self):
    """Tests scalar v2 invocation with no writer."""
    with self.assertWarnsRegex(
        UserWarning, 'default summary writer not found'):
      with test.mock.patch.object(
          summary_v2, 'scalar', autospec=True) as mock_scalar_v2:
        summary_lib.scalar('float', constant_op.constant(2.5))
    mock_scalar_v2.assert_not_called()

  @test_util.run_v2_only
  def test_scalar_summary_v2__global_step_not_set(self):
    """Tests scalar v2 invocation when global step is not set."""
    with self.assertWarnsRegex(UserWarning, 'global step not set'):
      with test.mock.patch.object(
          summary_v2, 'scalar', autospec=True) as mock_scalar_v2:
        with summary_ops_v2.create_summary_file_writer(
            '/tmp/test').as_default():
          summary_lib.scalar('float', constant_op.constant(2.5))
    mock_scalar_v2.assert_not_called()

  @test_util.run_v2_only
  def test_scalar_summary_v2__family(self):
    """Tests `family` arg handling when scalar v2 is invoked."""
    with test.mock.patch.object(
        summary_v2, 'scalar', autospec=True) as mock_scalar_v2:
      with summary_ops_v2.create_summary_file_writer('/tmp/test').as_default(
          step=1):
        tensor = summary_lib.scalar(
            'float', constant_op.constant(2.5), family='otter')
    # Returns empty string.
    self.assertEqual(tensor.numpy(), b'')
    self.assertEqual(tensor.dtype, dtypes.string)
    mock_scalar_v2.assert_called_once_with(
        'otter/otter/float', data=constant_op.constant(2.5), step=1)

  @test_util.run_v2_only
  def test_scalar_summary_v2__family_w_outer_scope(self):
    """Tests `family` arg handling when there is an outer scope."""
    with test.mock.patch.object(
        summary_v2, 'scalar', autospec=True) as mock_scalar_v2:
      with summary_ops_v2.create_summary_file_writer('/tmp/test').as_default(
          step=1):
        with ops.name_scope_v2('sea'):
          tensor = summary_lib.scalar(
              'float', constant_op.constant(3.5), family='crabnet')
    # Returns empty string.
    self.assertEqual(tensor.numpy(), b'')
    self.assertEqual(tensor.dtype, dtypes.string)
    mock_scalar_v2.assert_called_once_with(
        'crabnet/sea/crabnet/float', data=constant_op.constant(3.5), step=1)

  @test_util.run_v2_only
  def test_scalar_summary_v2__v1_set_step(self):
    """Tests scalar v2 invocation when v1 step is set."""
    global_step = training_util.create_global_step()
    global_step.assign(1024)
    with test.mock.patch.object(
        summary_v2, 'scalar', autospec=True) as mock_scalar_v2:
      with summary_ops_v2.create_summary_file_writer('/tmp/test').as_default():
        i = constant_op.constant(2.5)
        tensor = summary_lib.scalar('float', i)
    # Returns empty string.
    self.assertEqual(tensor.numpy(), b'')
    self.assertEqual(tensor.dtype, dtypes.string)
    mock_scalar_v2.assert_called_once_with('float', data=i, step=1024)


if __name__ == '__main__':
  test.main()
