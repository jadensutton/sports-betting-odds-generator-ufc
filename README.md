This is a web application meant to serve a Random Forest model I built to generate odds for UFC matches. To use, simply select two fighters and click to generate odds.

The performance metrics for the model are as follows:
1. Classification accuracy - 69%
1. Log loss - 0.54

Please note the following limitations of the model:
1. The model cannot account for instances where a fighter from one weight class is matched up against a fighter from a different weight class. In such instances, the
model will treat both fighters as if they're in the same weight class. I chose to not account for weight class differences, as there are not enough instances of fighters
fighting above/below their usual weight class in order to reliably account for it in predictions. Additionally, some fighters will move up or down in weight class
over the course of their career, and considering their current listed weight class as a factor while analyzing past fights in different weight classes could lead to 
look-ahead bias.
2. Due to unreliable and incomplete data provided by other promotions, the model does not consider data from any fights outside of the UFC. Fighters must have at least 5
fights listed on their UFC stats page in order to generate predictions. Additionally, predictions may be substantially inaccurate in cases where a fighter has had
mixed results within the UFC, but has had stellar results outside the UFC. This is because their stats accrued outside the UFC cannot be considered. For example, the
model tends to generate odds for Michael Chandler that are far lower than those offered by bookmakers. 

Disclaimer: This model was built strictly for educational purposes and as a hobby project. I do not encourage using this model to make betting decisions, and I bare no 
responsibility for anyone who chooses to do so.
