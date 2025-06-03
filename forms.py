from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField
from wtforms.validators import InputRequired, Optional

class tickerForm(FlaskForm):
	ticker = StringField('ticker', validators=[InputRequired()])
	tail = SelectField('tail', choices=[ ('auto','Auto'),('left','Left'), ('right','Right')],default='auto',validators=[Optional()])
	return_=DecimalField(number_format='%. 2f', validators=[Optional()])
	period= SelectField('period', choices=[ ('5d','5 Days'),('1mo','1 Month'), ('3mo','3 Months'), ('6mo', '6 Months'),('1y', '1 Year'),
						('2y', '2 Years'),('5y', '5 Years'),('10y', '10 Years'),('ytd', 'YTD'),('max', 'Max')],default='auto',validators=[InputRequired()])


