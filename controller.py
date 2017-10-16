from openerp.osv import osv, fields

class course(osv.Model):
	_name = 'academic.course'
	_columns = {
				'name'  			: fields.char('Name', size=50, required=True),
				'description'		: fields.text('Description'),
				'responsible_id'	: fields.many2one('res.users', string='Responsible'),
				'session_ids'		: fields.one2many('academic.session','course_id','Sessions',ondelete="cascade"),
				}

SESSION_STATES = [('draft','Draft'),('confirmed','Confirmed'),('done','Done')]

class session(osv.Model):
	_name = 'academic.session'

	def _calc_taken_seats(self, cr, uid, ids, field, arg, context=None):
			results = {}

			sessions = self.browse(cr,uid, ids, context=context)

			for session in sessions:
				if session.seats:
					results[session.id] = 100.0 * len(session.attendee_ids)/session.seats
				else:
					results[session.id] = 0.0

			return results

	def onchange_seats(self, cr, uid, ids, seats, attendee_ids):
		array_of_attendees = self.resolve_o2m_commands_to_record_dicts(cr, uid, 'attendee_ids', attendee_ids,['id'])
		results = {
			'value' : {
			'taken_seats' : 100.0 * len(array_of_attendees)/seats}}
		if seats < 0 :
			results['warning'] = {
				'title'   : 'Warning: Bad Seats Value',
				'message' : 'Please Enter Positive Number'}
		elif seats < len(array_of_attendees):
			results['warning'] = {
				'title'   : 'Warning: Bad Seats Value',
				'message' : 'Please Enter More Seats Number'}
		return results

	def action_draft(self, cr, uid, ids, context=None):
		return self.write(cr,uid,ids,{'state':SESSION_STATES[0][0]},context=context)

	def action_confirm(self, cr, uid, ids, context=None):
		return self.write(cr,uid,ids,{'state':SESSION_STATES[1][0]},context=context)

	def action_done(self, cr, uid, ids, context=None):
		return self.write(cr,uid,ids,{'state':SESSION_STATES[2][0]},context=context)

		_sql_constraints= [
							('name_description_check','CHECK(name <> description)','The Title of Course Should be Different Of The Description'),
							('name_unique','UNIQUE(name)','The Title Must be Unique')]
		_defaults = {
						
						'active' 	 : True,
						'start_date' : lambda *a : time.strftime("%y-%m-%d"),
						'state'		 : SESSION_STATES[0][0],
						}
		_sql_constraints= [
							('partner_session_unique','UNIQUE(partner_id, session_id)','You Can Not Insert the same Attendee Multiple time!')]

	_columns = {
				'course_id'  		: fields.many2one('academic.course', 'Course'),
				'instructor_id'		: fields.many2one('res.partner','Instructor'),
				'name'				: fields.char('Session Name',size=100,required=True),
				'start_date'		: fields.date('Start Date', required=True),
				'duration'			: fields.integer('Duration'),
				'seats'				: fields.integer('Nummber of Seats'),
				'active'			: fields.boolean('Is Active'),
				'attendee_ids'		: fields.one2many('academic.attendee','session_id', ondelete="cascade"),
				'taken_seats'		: fields.function(_calc_taken_seats, type='float', string="Taken Seats"),
				'image_small'		: fields.binary('Image Small'),
				'state' 			: fields.selection(SESSION_STATES,'Status', readonly=True,required=True),
				}

class attendee(osv.Model):
	_name = 'academic.attendee'
	_columns = { 'session_id'  		: fields.many2one('academic.session', 'Session'),
				 'partner_id'		: fields.many2one('res.partner','Partner'),
				 'name'				: fields.char('Name',size=100),
				 'course_id'		: fields.related('session_id','course_id', type='many2one', relation='academic.course', string='Course', store=True)}


class partner(osv.Model):
	_name 	 = 'res.partner'
	_inherit = 'res.partner'
	_columns = {	
				'is_instructor'	: fields.boolean('Is Instructor')}