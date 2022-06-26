# CovidLogWastewaterPlots

COVID case counts have been harder to track since home test kits have become more abundant, so COVID wastewater levels have become a better metric to estimate current trends in COVID prevalence. One of the issues with graphing wastewater trends and COVID case counts has been the extremely high level of COVID during the 2022 Omicron peak; on linear charts, the sheer scale of the Omicron peak makes everything else nearly flat. Some news outlets have compensated by only showing data after the Omicron peak, but this makes it hard to compare current COVID levels against those prior to the Omicron peak such as the January 2021 peak and the initial COVID wave. One solution to this problem is to use log scale. 

This package takes data from the Biobot Analytics Wastewater Github repository and has several functions to easily plot in both log and linear scales. I have hard-coded it to chart Suffolk County and Middlesex County (Boston and Cambridge, MA respectively), post these plots on Reddit r/CoronavirusMA, and email myself a notification. With the .bat file, I have setup my Windows task scheduler to run this every morning and make plots/post on Reddit/email myself if the Biobot Gihub includes new data for Suffolk County. 

If there's sufficient interest, I may put in more effort to separate out the functions and make the code more usable for others. 
