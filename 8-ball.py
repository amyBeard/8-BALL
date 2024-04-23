from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qsl
import sys
import cgi
import os
import Physics
import math
import glob
import random
import json

class MyHandler( BaseHTTPRequestHandler ):

    game = None
    game_name = None
    player1_name = None
    player2_name = None
    t_table = None
    vel_x = None
    vel_y = None
    db = None
    table_id = 0
    curr_player = None
    high_balls = None
    low_balls = None
    balls = set(range(16))

    def write_svg( self, table_id, table ):
        with open( "table%02d.svg" % table_id, "w" ) as fp:
            fp.write( table.svg() );
    
    def nudge( self ):
        return random.uniform( -1.5, 1.5 );
    #based on labserver.py from LAB2
    
    def do_GET( self ):

        parsed  = urlparse( self.path )

        if parsed.path in [ '/8-ball.html' ]:
            
            fp = open( '.'+self.path )
            content = fp.read()

            self.send_response( 200 ); 
            self.send_header( "Content-type", "text/html" )
            self.send_header( "Content-length", len( content ) )
            self.end_headers()

            self.wfile.write( bytes( content, "utf-8" ) )
            fp.close()

        elif parsed.path in [ '/display.html' ]:
            
            self.send_response( 200 ); 
            self.send_header( "Content-type", "text/html" )
            self.end_headers()

        elif parsed.path in [ '/styles.css' ]:

            fp = open( '.'+self.path )
            content = fp.read()

            self.send_response( 200 ); 
            self.send_header( "Content-type", "text/css" )
            self.send_header( "Content-length", len( content ) )
            self.end_headers()

            self.wfile.write( bytes( content, "utf-8" ) )
            fp.close()

        elif parsed.path in [ '/styles2.css' ]:

            fp = open( '.'+self.path )
            content = fp.read()

            self.send_response( 200 ); 
            self.send_header( "Content-type", "text/css" )
            self.send_header( "Content-length", len( content ) )
            self.end_headers()

            self.wfile.write( bytes( content, "utf-8" ) )
            fp.close()

        elif parsed.path.startswith("/table") and parsed.path.endswith(".svg"):

            
            with open( '.'+parsed.path, 'rb' ) as fp:
                content = fp.read()

            self.send_response( 200 )
            self.send_header( "Content-type", "image/svg+xml" )
            self.send_header( "Content-length", len( content ) )
            self.end_headers()

            self.wfile.write( content )
            fp.close()

        else:
            self.send_response( 404 )
            self.end_headers()
            self.wfile.write( bytes( "404: %s not found" % self.path, "utf-8" ) )

    def do_POST( self ):

        parsed  = urlparse( self.path )

        if self.path == '/shoot':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = dict(parse_qsl(post_data))
            MyHandler.vel_x = float(params.get("vel_x"))
            MyHandler.vel_y = float(params.get("vel_y"))

            print("WRITING TO DATABASE")
            MyHandler.game.shoot(MyHandler.game_name, MyHandler.curr_player, MyHandler.t_table, MyHandler.vel_x, MyHandler.vel_y)
            print("DATABASE WRITTEN")

            self.send_response(200)  # OK
            self.end_headers()
            return

        if self.path == '/get-svgs':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = dict(parse_qsl(post_data))
            req_time = float(params.get("time"))
            if (MyHandler.db != None):

                # table_id = 0
                # table = MyHandler.db.readTable(table_id)
                # while table:
                #     if not table:
                #         self.send_response(200)  # OK
                #         self.end_headers()
                #         return
                #     if round(table.time, 3) == req_time:
                #         print("writing new svg")
                #         self.write_svg(0, table)
                #         self.send_response(200)  # OK
                #         self.end_headers()
                #         return
                #     table_id += 1
                #     table = MyHandler.db.readTable(table_id)

                table = MyHandler.db.readTable(MyHandler.table_id)
                if table:
                    MyHandler.t_table = table
                    print("writing new svg")
                    self.write_svg(0, table)
                    MyHandler.table_id += 1
                    self.send_response(200)  # OK
                    self.end_headers()
                    return
            
            self.send_response(404)
            self.end_headers()
            return

        if self.path == '/get-table':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')

            table = MyHandler.db.readTable(MyHandler.table_id-1)
            switch = True
            curr_balls = set()
            winner = None

            for ball in table:
                if isinstance( ball, Physics.StillBall ):
                    curr_balls.add(ball.obj.still_ball.number)

            missing_balls = MyHandler.balls - curr_balls

            if (MyHandler.high_balls is None and missing_balls is not None):
                for ball_number in missing_balls:
                    if 0 < ball_number < 8:
                        if MyHandler.curr_player == MyHandler.player1_name:
                            MyHandler.low_balls = 0
                            MyHandler.high_balls = 1
                        else:
                            MyHandler.low_balls = 1
                            MyHandler.high_balls = 0
                        switch = False
                    elif ball_number > 8:
                        if MyHandler.curr_player == MyHandler.player1_name:
                            MyHandler.low_balls = 1
                            MyHandler.high_balls = 0
                        else:
                            MyHandler.low_balls = 0
                            MyHandler.high_balls = 1
                        switch = False
                    if ball_number == 8:
                        print("8-ball knocked in")
                        if MyHandler.curr_player == MyHandler.player1_name:
                            winner = MyHandler.player2_name
                        else:
                            winner = MyHandler.player1_name
                        switch = False
                        break
                    if ball_number == 0:
                        pos = Physics.Coordinate( Physics.TABLE_WIDTH/2.0 + random.uniform( -3.0, 3.0 ),
                                        Physics.TABLE_LENGTH - Physics.TABLE_WIDTH/2.0 )
                        sb  = Physics.StillBall( 0, pos )

                        MyHandler.t_table += sb
                        self.write_svg(0, MyHandler.t_table)
                        curr_balls.add(sb.obj.still_ball.number)
                        switch = True
                        break
                    break
            else:
                for ball_number in missing_balls:
                    print(missing_balls)
                    if 0 < ball_number < 8:
                        if MyHandler.low_balls == 0 and MyHandler.curr_player == MyHandler.player1_name:
                            switch = False
                        elif  MyHandler.low_balls == 1 and MyHandler.curr_player == MyHandler.player2_name:
                            switch = False
                    elif ball_number > 8:
                        if MyHandler.high_balls == 0 and MyHandler.curr_player == MyHandler.player1_name:
                            switch = False
                        elif  MyHandler.high_balls == 1 and MyHandler.curr_player == MyHandler.player2_name:
                            switch = False
                    if ball_number == 8:
                        # print("8-ball knocked in")
                        if MyHandler.curr_player == MyHandler.player1_name:
                            if MyHandler.low_balls == 0:
                                high = set(range(9,15))
                                high.add(0)
                                if len(curr_balls - high) == 0:
                                    winner = MyHandler.player1_name
                            elif MyHandler.high_balls == 0:
                                low = set(range(0,8))
                                if len(curr_balls - low) == 0:
                                    winner = MyHandler.player1_name
                            winner = MyHandler.player2_name
                        else:
                            if MyHandler.low_balls == 1:
                                high = set(range(9,15))
                                high.add(0)
                                print(curr_balls - high) 
                                if len(curr_balls - high) == 0:
                                    winner = MyHandler.player2_name
                            elif MyHandler.high_balls == 1:
                                low = set(range(0,8))
                                if len(curr_balls - low) == 0:
                                    winner = MyHandler.player2_name
                            winner = MyHandler.player1_name
                        switch = False
                        break
                    if ball_number == 0:
                        pos = Physics.Coordinate( Physics.TABLE_WIDTH/2.0 + random.uniform( -3.0, 3.0 ),
                                        Physics.TABLE_LENGTH - Physics.TABLE_WIDTH/2.0 )
                        sb  = Physics.StillBall( 0, pos )

                        MyHandler.t_table += sb
                        self.write_svg(0, MyHandler.t_table)
                        curr_balls.add(sb.obj.still_ball.number)
                        switch = True
                        break
                    break

            MyHandler.balls = curr_balls            

            if switch:
                if MyHandler.curr_player == MyHandler.player1_name:
                    MyHandler.curr_player = MyHandler.player2_name
                else:
                    MyHandler.curr_player = MyHandler.player1_name

            self.send_response(200)  # OK
            self.send_header("Content-type", "application/json")
            self.end_headers()
            print(winner)
            response_data = {"current_player": MyHandler.curr_player, "high": MyHandler.high_balls, "low": MyHandler.low_balls, "winner": winner}
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
            return


        if parsed.path in [ '/display.html' ]:
            
            
            if (MyHandler.db == None):
                print("MAKING NEW DB")
                form = cgi.FieldStorage( fp=self.rfile,
                                     headers=self.headers,
                                     environ = { 'REQUEST_METHOD': 'POST',
                                                 'CONTENT_TYPE': 
                                                   self.headers['Content-Type'],
                                               } 
                                   )
                #get form data
                form_data = {}
                for field in form.keys():
                    form_data = {field: form[field].value}

                MyHandler.game_name = form['gameName'].value
                MyHandler.player1_name = form['player1Name'].value
                MyHandler.player2_name = form['player2Name'].value
                MyHandler.vel_x = 0.0
                MyHandler.vel_y = 0.0
                MyHandler.curr_player = MyHandler.player1_name
                
                for file in os.listdir('.'):
                    if file.startswith('table') and file.endswith('.svg'):
                        os.remove(file)
                    if file.endswith('.db'):
                        os.remove(file)

                MyHandler.db = Physics.Database( reset = True);
                MyHandler.db.createDB();

                MyHandler.t_table = Physics.Table();

                # cue ball also still
                pos = Physics.Coordinate( Physics.TABLE_WIDTH/2.0 + random.uniform( -3.0, 3.0 ),
                                        Physics.TABLE_LENGTH - Physics.TABLE_WIDTH/2.0 );
                sb  = Physics.StillBall( 0, pos );

                MyHandler.t_table += sb;

                # 1 ball
                pos = Physics.Coordinate( 
                                Physics.TABLE_WIDTH / 2.0,
                                Physics.TABLE_WIDTH / 2.0,
                                );

                sb = Physics.StillBall( 1, pos );
                MyHandler.t_table += sb;

                # 2 ball
                pos = Physics.Coordinate(
                                Physics.TABLE_WIDTH/2.0 - (Physics.BALL_DIAMETER+4.0)/2.0 +
                                self.nudge(),
                                Physics.TABLE_WIDTH/2.0 - 
                                math.sqrt(3.0)/2.0*(Physics.BALL_DIAMETER+4.0)
                                );
                sb = Physics.StillBall( 2, pos );
                MyHandler.t_table += sb;

                # 3 ball
                pos = Physics.Coordinate(
                                Physics.TABLE_WIDTH/2.0 + (Physics.BALL_DIAMETER+6.0)/2.0 +
                                self.nudge(),
                                Physics.TABLE_WIDTH/2.0 - 
                                math.sqrt(3.0)/2.0*(Physics.BALL_DIAMETER+4.0)
                                );
                sb = Physics.StillBall( 3, pos );
                MyHandler.t_table += sb;

                # 4 ball
                pos = Physics.Coordinate(
                                Physics.TABLE_WIDTH/2.0 - (2*Physics.BALL_DIAMETER+6.0)/2 +
                                self.nudge(),
                                Physics.TABLE_WIDTH/2.0 - 
                                math.sqrt(3.0)/2.0*(2*Physics.BALL_DIAMETER+8.0)
                                );

                sb = Physics.StillBall( 4, pos );
                MyHandler.t_table += sb;

                #5 ball
                pos = Physics.Coordinate(
                                Physics.TABLE_WIDTH/2.0 - (Physics.BALL_RADIUS + 4.0) +
                                self.nudge(),
                                Physics.TABLE_WIDTH/2.0 - 
                                math.sqrt(3.0)/2.0*(3*Physics.BALL_DIAMETER + 16.0)
                                );
                sb = Physics.StillBall( 5, pos );
                MyHandler.t_table += sb;

                # 6 ball
                pos = Physics.Coordinate(
                                Physics.TABLE_WIDTH/2.0 + (2*Physics.BALL_DIAMETER+6.0)/2 +
                                self.nudge(),
                                Physics.TABLE_WIDTH/2.0 - 
                                math.sqrt(3.0)/2.0*(2*Physics.BALL_DIAMETER+8.0)
                                );

                sb = Physics.StillBall( 6, pos );
                MyHandler.t_table += sb;


                # 7 ball
                pos = Physics.Coordinate(
                                Physics.TABLE_WIDTH/2.0 - (3*Physics.BALL_RADIUS + 8.0) +
                                self.nudge(),
                                Physics.TABLE_WIDTH/2.0 - 
                                math.sqrt(3.0)/2.0*(3*Physics.BALL_DIAMETER+16.0)
                                );
                sb = Physics.StillBall( 7, pos );
                MyHandler.t_table += sb;

                # 8 ball
                pos = Physics.Coordinate(
                                Physics.TABLE_WIDTH/2.0+
                                self.nudge(),
                                Physics.TABLE_WIDTH/2.0 - 
                                math.sqrt(3.0)/2.0*(2*Physics.BALL_DIAMETER+8.0)
                                );

                sb = Physics.StillBall( 8, pos );
                MyHandler.t_table += sb;

                # 9 ball
                pos = Physics.Coordinate(
                                Physics.TABLE_WIDTH/2.0 + (Physics.BALL_RADIUS + 4.0) +
                                self.nudge(),
                                Physics.TABLE_WIDTH/2.0 - 
                                math.sqrt(3.0)/2.0*(3*Physics.BALL_DIAMETER+16.0) +
                                self.nudge()
                                );
                sb = Physics.StillBall( 9, pos );
                MyHandler.t_table += sb;

                # 10 ball
                pos = Physics.Coordinate(
                                Physics.TABLE_WIDTH/2.0 + (3*Physics.BALL_RADIUS + 8.0) +
                                self.nudge(),
                                Physics.TABLE_WIDTH/2.0 - 
                                math.sqrt(3.0)/2.0*(3*Physics.BALL_DIAMETER+16.0)
                                );
                sb = Physics.StillBall( 10, pos );
                MyHandler.t_table += sb;

                # 11 ball
                pos = Physics.Coordinate(
                                Physics.TABLE_WIDTH/2.0 - (4*Physics.BALL_RADIUS + 12.0) +
                                self.nudge(),
                                Physics.TABLE_WIDTH/2.0 - 
                                math.sqrt(3.0)/2.0*(4*Physics.BALL_DIAMETER + 24.0)
                                );

                sb = Physics.StillBall( 11, pos );
                MyHandler.t_table += sb;

                # 12 ball
                pos = Physics.Coordinate(
                                Physics.TABLE_WIDTH/2.0 - (Physics.BALL_DIAMETER + 4.0) +
                                self.nudge(),
                                Physics.TABLE_WIDTH/2.0 - 
                                math.sqrt(3.0)/2.0*(4*Physics.BALL_DIAMETER + 24.0)
                                );

                sb = Physics.StillBall( 12, pos );
                MyHandler.t_table += sb;

                #13 ball
                pos = Physics.Coordinate(
                                Physics.TABLE_WIDTH/2.0 +
                                self.nudge(),
                                Physics.TABLE_WIDTH/2.0 - 
                                math.sqrt(3.0)/2.0*(4*Physics.BALL_DIAMETER + 24.0)
                                );

                sb = Physics.StillBall( 13, pos );
                MyHandler.t_table += sb;

                # # 14 ball
                pos = Physics.Coordinate(
                                Physics.TABLE_WIDTH/2.0 + (Physics.BALL_DIAMETER+4.0) +
                                self.nudge(),
                                Physics.TABLE_WIDTH/2.0 - 
                                math.sqrt(3.0)/2.0*(4*Physics.BALL_DIAMETER + 24.0)
                                );

                sb = Physics.StillBall( 14, pos );
                MyHandler.t_table += sb;

                # # 15 ball
                pos = Physics.Coordinate(
                                Physics.TABLE_WIDTH/2.0 + (4*Physics.BALL_RADIUS + 12.0) +
                                self.nudge(),
                                Physics.TABLE_WIDTH/2.0 - 
                                math.sqrt(3.0)/2.0*(4*Physics.BALL_DIAMETER + 24.0)
                                );

                sb = Physics.StillBall( 15, pos );
                MyHandler.t_table += sb;

                self.write_svg( 0, MyHandler.t_table );
                MyHandler.game = Physics.Game( gameName= MyHandler.game_name, player1Name= MyHandler.player1_name, player2Name= MyHandler.player2_name )

            else:
                print("Database already written")

            content = """<html><head><title>8-BALL</title><link rel="stylesheet" href="./styles2.css"></head><body>"""

            content += '<div class ="header">'
            content += f'<h1 id = "gameName" >{MyHandler.game_name}</h1>'
            content += f'<h2 id="playerNames"><span class="player1_class">{MyHandler.player1_name}</span> vs. <span class="player2_class">{MyHandler.player2_name}</span></h2>'
            content += f"""<p id = "curr_players">{MyHandler.curr_player}'s turn.</p>"""
            content +='</div>'
            # Container for the SVG
            content += '<div id="svg_container"></div>'

            content += """
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <script>
            $(document).ready(function() {
                var isDrawing = false;
                var svg_file = "table00.svg"; // Assuming the initial SVG file name

                function loadSVG() {
                    $("#svg_container").load(svg_file, function() {
                        // Add event listener to cue ball
                        $("#svg_container").on("mousedown", "circle", function(event) {
                            if ($(this).attr("fill") === "WHITE" && !isDrawing) {
                                isDrawing = true;
                                var offset_x = $(this).attr("cx") / event.pageX;
                                var offset_y = $(this).attr("cy") / event.pageY;
                                var startX = event.pageX * offset_x;
                                var startY = event.pageY * offset_y;

                                var line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                                line.setAttribute("stroke", "tan");
                                line.setAttribute("stroke-width", 10);
                                line.setAttribute("id", "line");
                                line.setAttribute("x1", startX);
                                line.setAttribute("y1", startY);
                                line.setAttribute("x2", startX);
                                line.setAttribute("y2", startY);
                                line.dataset.vel_x = 0;
                                line.dataset.vel_y = 0;

                                $("#svg_container svg").append(line);

                                $(document).on("mousemove", function(event) {
                                    if (isDrawing) {
                                        var endX = event.pageX * offset_x;
                                        var endY = event.pageY * offset_y;

                                        // Update line coordinates
                                        $("#line").attr("x2", endX);
                                        $("#line").attr("y2", endY);

                                        line.dataset.vel_x = startX - endX;
                                        line.dataset.vel_y = startY - endY;
                                    }
                                });

                                $(document).on("mouseup", function() {
                                    if (isDrawing) {
                                        isDrawing = false;
                                        var x2 = $('#line').attr("x2");
                                        var y2 = $('#line').attr("y2");
                                        //console.log(x2, y2);

                                        var vel_x = parseFloat($('#line').data("vel_x"));
                                        var vel_y = parseFloat($('#line').data("vel_y"));
                                        //console.log(vel_x, vel_y);
                                        $('#line').hide();
                                        
                                        function tableStatus(){
                                            $.ajax({
                                                type: "POST",
                                                url: "/get-table",
                                                success: function(response){
                                                    $('#curr_players').text(response.current_player + "'s turn.");
                                                    if (response.low == 0){
                                                        $('.player1_class').addClass("deeppink-text");
                                                        $('.player2_class').addClass("gold-text");
                                                    }else if (response.low == 1){
                                                        $('.player1_class').addClass("gold-text");
                                                        $('.player2_class').addClass("deeppink-text");
                                                    }
                                                    if (response.winner){
                                                        console.log("Trying to display winner");
                                                        var winner_text = document.createElement("h1");
                                                        winner_text.setAttribute("id", "winner");
                                                        const textNode = document.createTextNode(response.winner + " wins!");
                                                        winner_text.appendChild(textNode);
                                                        $("#svg_container").remove(svg_file);
                                                        $("#curr_players").hide();
                                                        $("#svg_container").html(winner_text);
                                                        //return false;
                                                    }
                                                },
                                                error: function(xhr, status, error) {
                                                    console.error("Error getting game state:", error);
                                                }
                                            });
                                        }
                                        
                                        function animateShot(time) {
                                            $.ajax({
                                                type: "POST",
                                                url: "/get-svgs",
                                                data: { time: time },
                                                success: function() {

                                                    $("#svg_container").load("table00.svg");

                                                    var nextTime = time + 0.01; 
                                                    
                                                    animateShot(nextTime);
                                                },
                                                error: function(xhr, status, error) {
                                                    alert("You can take another shot")
                                                    tableStatus()
                                                    //assign colours off first sunken ball (might add an alert along with the colours)
                                                    //need to check if any balls were sunk, player gets another turn if they sunk one of theres
                                                    // check if white ball is still on table, if not reassign to original position
                                                    // check if 'black' ball is still on table, if the player has no other balls left, they win. otherwise they lose
                                                    //REMEMBER YOU NEED TO SWITCH THE OLAYER VAR IN GAME.SHOT WHEN YOU CALL IT
                                                    loadSVG();
                                                }
                                            });
                                        }

                                        $.ajax({
                                            type: "POST",
                                            url: "/shoot",
                                            data: {
                                                vel_x: vel_x * 4,
                                                vel_y: vel_y * 4
                                            },
                                            success: function () {
                                                animateShot(0.0);
                                            },
                                            error: function (xhr, status, error) {
                                                console.error("Error shooting:", error);
                                            }
                                        });

                                        $(document).off("mousemove");
                                    }
                                });
                            }
                        });
                    });
                }

                loadSVG(); // Load the initial SVG file
            });
            </script>"""

            
            content += '</body></html>'  


            # generate the headers
            self.send_response(200)  # OK
            self.send_header("Content-type", "text/html")
            self.send_header("Content-length", len(content))
            self.end_headers()

            # send it to the browser
            self.wfile.write(bytes(content, "utf-8"))   

        else:
            # generate 404
            self.send_response( 404 )
            self.end_headers()
            self.wfile.write( bytes( "404: %s not found" % self.path, "utf-8" ) )

        

if __name__ == "__main__":
    httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), MyHandler )
    print( "Server listing in port:  ", int(sys.argv[1]) )
    httpd.serve_forever()