import streamlit as st
from datetime import datetime, timedelta
import uuid
import calendar
import pandas as pd

from components.styles import apply_styles
from components.matrix import render_matrix
from services.loaders import load_data, load_metric_file
from services.aggregations import aggregate_actual_defaults, aggregate_metric_defaults
from services.project_leaders import PROJECT_LEADERS
