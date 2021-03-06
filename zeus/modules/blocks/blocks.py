# -*- coding:utf-8 -*-

# Copyright (C) 2020. Huawei Technologies Co., Ltd. All rights reserved.
# This program is free software; you can redistribute it and/or modify
# it under the terms of the MIT License.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# MIT License for more details.

"""This is SearchSpace for blocks."""
from zeus.common import ClassType, ClassFactory
from zeus.modules.module import Module
from zeus.modules.connections import Add
from zeus.modules.operators import ops


@ClassFactory.register(ClassType.SEARCH_SPACE)
class ShortCut(Module):
    """Create Shortcut SearchSpace."""

    def __init__(self, inchannel, outchannel, expansion, stride=1):
        """Create ShortCut layer.

        :param inchannel: input channel.
        :type inchannel: int
        :param outchannel: output channel.
        :type outchannel: int
        :param expansion: expansion
        :type expansion: int
        :param stride: the number to jump, default 1
        :type stride: int
        """
        super(ShortCut, self).__init__()
        if stride != 1 or inchannel != outchannel * expansion:
            self.conv1 = ops.Conv2d(in_channels=inchannel, out_channels=outchannel * expansion, kernel_size=1,
                                    stride=stride, bias=False)
            self.batch = ops.BatchNorm2d(num_features=outchannel * expansion)


@ClassFactory.register(ClassType.SEARCH_SPACE)
class BottleConv(Module):
    """Create BottleConv Searchspace."""

    def __init__(self, inchannel, outchannel, expansion, groups, base_width, stride=1):
        """Create BottleConv layer.

        :param inchannel: input channel.
        :type inchannel: int
        :param outchannel: output channel.
        :type outchannel: int
        :param expansion: expansion
        :type expansion: int
        :param stride: the number to jump, default 1
        :type stride: int
        """
        super(BottleConv, self).__init__()
        outchannel = int(outchannel * (base_width / 64.)) * groups
        self.conv1 = ops.Conv2d(in_channels=inchannel, out_channels=outchannel, kernel_size=1, stride=1, bias=False)
        self.batch1 = ops.BatchNorm2d(num_features=outchannel)
        self.conv2 = ops.Conv2d(in_channels=outchannel, out_channels=outchannel, kernel_size=3, stride=stride,
                                padding=1, groups=groups, bias=False)
        self.batch2 = ops.BatchNorm2d(num_features=outchannel)
        self.conv3 = ops.Conv2d(in_channels=outchannel, out_channels=outchannel * expansion, kernel_size=1, stride=1,
                                bias=False)
        self.batch3 = ops.BatchNorm2d(num_features=outchannel * expansion)
        self.relu = ops.Relu()


@ClassFactory.register(ClassType.SEARCH_SPACE)
class BasicConv(Module):
    """Create BasicConv Searchspace."""

    def __init__(self, inchannel, outchannel, groups=1, base_width=64, stride=1):
        """Create BasicConv layer.

        :param inchannel: input channel.
        :type inchannel: int
        :param outchannel: output channel.
        :type outchannel: int
        :param stride: the number to jump, default 1
        :type stride: int
        """
        super(BasicConv, self).__init__()
        self.conv = ops.Conv2d(in_channels=inchannel, out_channels=outchannel, kernel_size=3, stride=stride,
                               padding=1, groups=groups, bias=False)
        self.batch = ops.BatchNorm2d(num_features=outchannel)
        self.relu = ops.Relu(inplace=True)
        self.conv2 = ops.Conv2d(in_channels=outchannel, out_channels=outchannel, kernel_size=3,
                                padding=1, groups=groups, bias=False)
        self.batch2 = ops.BatchNorm2d(num_features=outchannel)


@ClassFactory.register(ClassType.SEARCH_SPACE)
class SmallInputInitialBlock(Module):
    """Create SmallInputInitialBlock SearchSpace."""

    def __init__(self, init_plane):
        """Create SmallInputInitialBlock layer.

        :param init_plane: input channel.
        :type init_plane: int
        """
        super(SmallInputInitialBlock, self).__init__()
        self.conv = ops.Conv2d(in_channels=3, out_channels=init_plane, kernel_size=3, stride=1,
                               padding=1, bias=False)
        self.bn = ops.BatchNorm2d(num_features=init_plane)
        self.relu = ops.Relu()


@ClassFactory.register(ClassType.SEARCH_SPACE)
class InitialBlock(Module):
    """Create InitialBlock SearchSpace."""

    def __init__(self, init_plane):
        """Create InitialBlock layer.

        :param init_plane: input channel.
        :type init_plane: int
        """
        super(InitialBlock, self).__init__()
        self.conv = ops.Conv2d(in_channels=3, out_channels=init_plane, kernel_size=7, stride=2, padding=3,
                               bias=False)
        self.batch = ops.BatchNorm2d(num_features=init_plane)
        self.maxpool2d = ops.MaxPool2d(kernel_size=3, stride=2, padding=1)


@ClassFactory.register(ClassType.SEARCH_SPACE)
class BasicBlock(Module):
    """Create BasicBlock SearchSpace."""

    expansion = 1

    def __init__(self, inchannel, outchannel, groups=1, base_width=64, stride=1):
        """Create BasicBlock layers.

        :param inchannel: input channel.
        :type inchannel: int
        :param outchannel: output channel.
        :type outchannel: int
        :param stride: the number to jump, default 1
        :type stride: int
        """
        super(BasicBlock, self).__init__()
        base_conv = BasicConv(inchannel=inchannel, outchannel=outchannel, stride=stride,
                              groups=groups, base_width=base_width)
        shortcut = ShortCut(inchannel=inchannel, outchannel=outchannel, expansion=self.expansion,
                            stride=stride)
        self.block = Add(base_conv, shortcut)
        self.relu = ops.Relu()


@ClassFactory.register(ClassType.SEARCH_SPACE)
class BottleneckBlock(Module):
    """Create BottleneckBlock SearchSpace."""

    expansion = 4

    def __init__(self, inchannel, outchannel, groups=1, base_width=64, stride=1):
        """Create BottleneckBlock layers.

        :param inchannel: input channel.
        :type inchannel: int
        :param outchannel: output channel.
        :type outchannel: int
        :param stride: the number to jump, default 1
        :type stride: int
        """
        super(BottleneckBlock, self).__init__()
        bottle_conv = BottleConv(inchannel=inchannel, outchannel=outchannel, expansion=self.expansion,
                                 stride=stride, groups=groups, base_width=base_width)
        shortcut = ShortCut(inchannel=inchannel, outchannel=outchannel, expansion=self.expansion, stride=stride)
        self.block = Add(bottle_conv, shortcut)
        self.relu = ops.Relu()


@ClassFactory.register(ClassType.SEARCH_SPACE)
class PruneBasicBlock(Module):
    """Basic block class in prune resnet."""

    expansion = 1

    def __init__(self, inchannel, outchannel, innerchannel, stride=1):
        """Init PruneBasicBlock."""
        super(PruneBasicBlock, self).__init__()
        conv_block = PruneBasicConv(inchannel, outchannel, innerchannel, stride)
        shortcut = ShortCut(inchannel, outchannel, self.expansion, stride)
        self.block = Add(conv_block, shortcut)
        self.relu3 = ops.Relu()


@ClassFactory.register(ClassType.SEARCH_SPACE)
class PruneBasicConv(Module):
    """Create PruneBasicConv Searchspace."""

    def __init__(self, in_planes, planes, inner_plane, stride=1):
        """Create BottleConv layer."""
        super(PruneBasicConv, self).__init__()
        self.conv1 = ops.Conv2d(
            in_planes, inner_plane, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = ops.BatchNorm2d(inner_plane)
        self.relu = ops.Relu()
        self.conv2 = ops.Conv2d(inner_plane, planes, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = ops.BatchNorm2d(planes)
        self.relu2 = ops.Relu()
