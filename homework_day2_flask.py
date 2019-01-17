from flask import Flask, redirect, url_for
from flask import request, render_template
from homework_day2_fn_cl import *

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        homeworkd1 = createDB()
        homeworkd1.clean()
        homeworkd1.run()
        tables = DB()
        tables.create_tables()

        db = 'dbready'
        return render_template("tabele.html", db=db)

    else:
        return render_template("index.html")


@app.route('/modify', methods=['GET', 'POST'])
def modify():
    t = request.args.get('tabela')

    if t:
        table_rows_1 = None
        table_rows_2 = None
        table_rows = None
        o1 = DB()
        sql = "Select * from {}".format(t)
        if t == 'shows':
            sql = '''select shows.id, movies.name as m_name, cinemas.name as c_name from shows inner join movies on
                     movies.id= shows.id_movie inner join cinemas on cinemas.id=shows.id_cinema;'''
        if t == 'tickets':
            sql_1 = 'Select * from tickets where exists(select 1 from payments where tickets.id=payments.ticket_id);'
            sql_2 = 'Select * from tickets where not exists(select 1 from payments where tickets.id=payments.ticket_id);'
            try:
                o1.select(sql_1)
                table_rows_1 = o1.data
                o1.select(sql_2)
                table_rows_2 = o1.data
            except OperationalError:
                createDB = True
                return render_template("tabele.html", createDB=createDB)
        else:
            try:
                o1.select(sql)
            except OperationalError:
                createDB = True
                return render_template("tabele.html", createDB=createDB)
            table_rows = o1.data

        if t == 'movies':
            for row in table_rows:
                sql = '''select distinct cinemas.name from shows inner join movies on movies.id= shows.id_movie 
                         inner join cinemas on cinemas.id=shows.id_cinema where movies.id={};'''.format(row['id'])
                o1.select(sql)
                cinemas = o1.data
                l = ', '.join([c['name'] for c in cinemas])
                row['cinemas'] = l
        if t == 'cinemas':
            for row in table_rows:
                sql = '''select distinct movies.name from shows inner join movies on movies.id= shows.id_movie 
                         inner join cinemas on cinemas.id=shows.id_cinema where cinemas.id={};'''.format(row['id'])
                o1.select(sql)
                movies = o1.data
                l = ', '.join([m['name'] for m in movies])
                row['movies'] = l

        if t == 'tickets':
            def rows_t(table_rows, ob):
                for row in table_rows:
                    sql = '''select shows.id, movies.name as m_name, cinemas.name as c_name from shows inner join movies on
                                     movies.id= shows.id_movie inner join cinemas on cinemas.id=shows.id_cinema where shows.id={};'''.format(
                        row['id_show'])
                    ob.select(sql)  # metoda klasy
                    show = ob.data
                    l = ['Id Show:{}- Movie: {}- Cinema: {}'.format(s['id'], s['m_name'], s['c_name']) for s in show]
                    row['show'] = l[0]

            rows_t(table_rows_1, o1)
            rows_t(table_rows_2, o1)

            return render_template("tabele.html", t=t, rows_1=table_rows_1, rows_2=table_rows_2)

        return render_template("tabele.html", t=t, rows=table_rows)
    else:
        return render_template('tabele.html')


@app.route('/delete/<string:table>/<int:rv>')
def delete(table, rv):
    del_row = ''

    try:
        select('Select 1;')
    except Exception:
        return redirect('/')
    o2 = DB()
    o2.delete(table, rv)

    if o2.id:
        del_row = 'Row with id={} was removed successfully from table {}'.format(rv, table)
    else:
        del_row = "Row with id={} doesn't exist in table {}".format(rv, table)

    return render_template("tabele.html", del_row=del_row)


@app.route('/new/<string:table>', methods=['GET', 'POST'])
def new(table):
    def show_form():
        sql_movies = "select id, name FROM movies"
        sql_cinemas = "select id, name FROM cinemas"
        movies = select(sql_movies)  # funkcja select
        cinemas = select(sql_cinemas)
        return [movies, cinemas]

    def t_form():
        sql = 'select shows.id, movies.name as m_name, cinemas.name as c_name from shows inner join movies on movies.id= shows.id_movie inner join cinemas on cinemas.id=shows.id_cinema;'
        table_rows = select(sql)
        return table_rows

    def p_form():
        sql = 'Select id from tickets where not exists(select 1 from payments where tickets.id=payments.ticket_id);'
        table_rows = select(sql)
        return table_rows

    if request.method == 'GET':
        try:
            select('Select 1;')
        except Exception:
            return redirect('/')

        if table == 'shows':
            mc_list = show_form()
            if not mc_list[0]:
                return redirect(url_for('new', table='movies'))
            elif not mc_list[1]:
                return redirect(url_for('new', table='cinemas'))

            return render_template('add_{}.html'.format(table), movies=mc_list[0], cinemas=mc_list[1])

        if table == 'tickets':
            if not t_form():
                return redirect(url_for('new', table='shows'))
            return render_template('add_{}.html'.format(table), shows=t_form())

        if table == 'payments':
            if not p_form():
                return redirect(url_for('new', table='tickets'))
            return render_template('add_{}.html'.format(table), tickets=p_form())

        return render_template('add_{}.html'.format(table))

    elif request.method == 'POST':
        v = []
        sql = None
        values = ()
        button = request.form['submit']
        if button == 'movies':
            n = request.form['name']
            d = request.form['desc']
            r = request.form['rating']
            v.append(data_validation(n, name=True))
            v.append(data_validation(r, float_number=True, rating=True))
            sql = "Insert into movies (name,description,rating) VALUES (%s,%s,%s)"
            values = (n, d, r)

        elif button == 'cinemas':
            n = request.form['name']
            a = request.form['address']
            c = request.form['capacity']
            v.append(data_validation(n, name=True))
            v.append(data_validation(c))
            sql = "Insert into cinemas (name,address,capacity) VALUES (%s,%s,%s)"
            values = (n, a, c)

        elif button == 'tickets':
            q = request.form['quantity']
            p = request.form['price']
            s = request.form['show']
            v.append(data_validation(q))
            v.append(data_validation(p, float_number=True))
            sql = "Insert into tickets (quantity,price,id_show) VALUES (%s,%s,%s) returning id"
            values = (q, p, s)

        elif button == 'payments':
            tid = request.form['ticket']
            tp = request.form['type']
            dt = request.form['date']
            sql = "Insert into payments (ticket_id,type,date ) VALUES (%s,%s,%s)"
            values = (tid, tp, dt)

        elif button == 'shows':
            m = request.form['movie']
            c = request.form['cinema']
            sql = "Insert into shows (id_movie,id_cinema ) VALUES (%s,%s)"
            values = (m, c)

        for e in v:
            if e:
                error = e
                if button == 'tickets':
                    return render_template('add_{}.html'.format(table), shows=t_form(), error=error)

                return render_template('add_{}.html'.format(button), error=error)

        o3 = DB()
        try:
            o3.insert(sql, values)
        # data error, integrity error, operational error
        except IntegrityError:
            error = 'Unique constraint Error. Table row already exists.'
            mc_list = show_form()
            return render_template('add_{}.html'.format(button), error=error, movies=mc_list[0], cinemas=mc_list[1])
        except DataError:
            error = 'Incorrect date'
            return render_template('add_{}.html'.format(table), tickets=p_form(), error=error)

        if button == 'tickets':
            id_value = o3.id[0]
            return redirect(url_for('pay_ticket', id=id_value))

        return render_template("tabele.html", button=button)


@app.route('/payment/<int:id>', methods=['GET'])
def payment_one(id):
    sql = 'Select * from payments where ticket_id={}'.format(id)
    row = select(sql)
    return render_template('tabele.html', t='payments', rows=row)


@app.route('/new/payments/<int:id>', methods=['GET', 'POST'])
def pay_ticket(id):
    if request.method == 'GET':
        try:
            select('Select 1;')
        except Exception:
            return redirect('/')
        tid = [{'id': id}]
        return render_template('add_payments.html', tickets=tid)
    elif request.method == 'POST':
        tid = request.form['ticket']
        tp = request.form['type']
        dt = request.form['date']
        sql = "Insert into payments (ticket_id,type,date ) VALUES (%s,%s,%s)"
        values = (tid, tp, dt)
        d_id = [{'id': tid}]
        o3 = DB()
        try:
            o3.insert(sql, values)
        except DataError:
            error = 'Incorrect date'
            return render_template('add_payments.html', error=error, tickets=d_id)

        return redirect(url_for('modify', tabela='tickets'))
        # return redirect('/new/payments') #?


@app.route('/payments_details', methods=['GET', 'POST'])
def pm_details():
    tt = ''
    type = None
    if request.method == 'GET':
        try:
            select('Select 1;')
        except Exception:
            return redirect('/')

        sql = 'select tickets.id, quantity, price, date,type from tickets inner join payments on tickets.id=payments.ticket_id'

        t = request.args.get('type')
        if t:
            tt = 'Tickets paid by {}'.format(t)
            x = " where type='{}'".format(t)
            sql = sql + x

        s = request.args.get('show1')
        if s:
            type = True
            x = " where id_show='{}'".format(s)
            sql = sql + x
            v2 = ''
            v = t_form()  #seanse
            for r in v:
                if r['id'] == int(s):
                    v2 = 'Id:{}- Movie:{}- Cinema:{}'.format(r['id'], r['m_name'], r['c_name'])

            tt = 'Tickets for Show: {}'.format(v2)

        return render_template('search.html', rows=select(sql), tt=tt, shows=t_form(), type=type)

    elif request.method == 'POST':

        t = ''
        sql = None
        dfrom = request.form.get('date_from')
        dto = request.form.get('date_to')
        d = request.form.get('date')
        x = """Search results:
        You searched for: {} : '{}'
        """
        # date
        if dfrom and dto:
            sql = "select * from payments where date BETWEEN '{}' and '{}' ORDER BY DATE".format(dfrom, dto)
            t = 'payments'
            date_between = str(dfrom) + ' and ' + str(dto)
            x = x.format('date beetwen', date_between)

        elif dfrom:
            sql = "select * from payments where date >= '{}' ORDER BY DATE ".format(dfrom)
            t = 'payments'
            x = x.format('date from', dfrom)

        elif dto:
            sql = "select * from payments where date <= '{}' ORDER BY DATE".format(dto)
            t = 'payments'
            x = x.format('date to', dto)

        elif d:
            sql = "select * from payments where date = '{}'".format(d)
            t = 'payments'
            x = x.format('date', d)

        if not t:
            return redirect('/payments_details')

        rv = select(sql)
        return render_template('search_results.html', t=t, rows=rv, x=x)


if __name__ == '__main__':
    app.run(debug=True)
