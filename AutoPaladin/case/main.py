# -*- coding:utf-8 -*-
import os, sys
import time

import pytest

from case import case_generator

if __name__ == '__main__':
    case_generator.generate_all('Saas')
    pytest.main(['-m', 'Saas', '-s'])
