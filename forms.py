from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField
from wtforms.validators import InputRequired, Optional

class tickerForm(FlaskForm):
	ticker = StringField('ticker', validators=[InputRequired()])
	tail = SelectField('tail', choices=[ ('auto','Auto'),('left','Left'), ('right','Right')],default='auto',validators=[Optional()])
	return_=DecimalField(number_format='%. 2f', validators=[Optional()])


