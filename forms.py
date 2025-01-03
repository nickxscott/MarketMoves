from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField
from wtforms.validators import InputRequired, Optional

class tickerForm(FlaskForm):
	ticker = StringField('ticker', validators=[InputRequired()])
	tail = SelectField('tail', choices=['left', 'right'],validators=[InputRequired()])
	return_=DecimalField(number_format='%. 2f', validators=[Optional()])


