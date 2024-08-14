from openfigipy import OpenFigiClient
import os
from langchain_core.tools import Tool, tool
from typing import Dict, Union, List


apikey = os.environ.get("OPENFIGI_KEY")
ofc = OpenFigiClient(api_key=apikey)
ofc.connect()


class OpenFigiTools:

    @tool("openfigi_get_ticker")
    def get_ticker(**kwargs):
        """Get the ticker given a company name
        Takes kwargs.
            - query is a mandatory key in this dictionary (put the company name 
            you want to search for under this key). 
            
            The other acceptable keys are: 
            - exchCode: for example, US, CH, or IN. If you know the exchange 
            code you are expecting, it helps narrowing down the results. 
            Defaults to `US`
            - securityType: Most common types are 
            'Common Stock', 'Prefered Stock', 'ADR'. Defaults to 'Common Stock'
        """
        if 'securityType' not in kwargs.keys():
            kwargs.update({"securityType": "Common Stock"})
        if 'exchCode' not in kwargs.keys():
            kwargs.update({"exchCode": "US"})
        assert "query" in kwargs.keys(), "the `query` key must be present!"
        results = ofc.search(**kwargs)
        results = results.rename({"securityDescription": "ticker"}, axis=1)
        return results