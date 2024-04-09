import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import pytz
import sqlite3
con = sqlite3.connect("week3.sqlite", isolation_level=None)
cur = con.cursor()