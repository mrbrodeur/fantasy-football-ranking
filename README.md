# Analysis of Analysts for Fantasy Football
We wanted to see how accurate fantasy football analysts were and also if any of them were better than any others. 

When looking at just fantasy football predictions for 'kickers', we found that there was no evidence that any analyst--or the 'overall rank' prediction--was any better than any of the other ones (p-value .9996!)

## Methodology

### Preparing the data
Data was scraped from Football DB box scores using Scrapy to create a dataset of each kicker's points for each game. For each week, each kicker was given a ranking based on their fantasy points for that week relative to the other kickers. 

Analyst predictions were taken from Fantasy Pros, which are also the 'experts' who are used for Yahoo sports. 

Because most fantasy football leagues are 12 teams, we only cared about the accuracy of the first 12 predictions. If the analyst/expert was good or bad at their predictions after 12, it isn't that important for a fantasy football league. 

