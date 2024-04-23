#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "phylib.h"

// export LD_LIBRARY_PATH='/Users/amybeard/Desktop/A4'

/*make new still ball given ball number and position coords
malloc memory for ball then assign position and number values.
if either are null return null, otherwise return the object*/
phylib_object *phylib_new_still_ball( unsigned char number,
phylib_coord *pos ){

    phylib_object * object = malloc(sizeof(phylib_object));
    //printf("MALLOC'D STILL BALL @ %p\n", (void *)object);
    if (object == NULL){
        return NULL;
    }

    object -> type = PHYLIB_STILL_BALL;
    object->obj.still_ball.number = number;
    if (pos == NULL){
        return NULL;
    }
    object->obj.still_ball.pos = *pos;

    return object;
}

/*make new rolling ball given ball number, position, acc, and vel coords.
malloc memory for ball then assign pos, acc, vel, and number values.
if either are null return null, otherwise return the object*/
phylib_object *phylib_new_rolling_ball( unsigned char number,
phylib_coord *pos,
phylib_coord *vel,
phylib_coord *acc ){

    phylib_object * object = malloc(sizeof(phylib_object));
    //printf("MALLOC'D ROLLING BALL @ %p\n", (void *)object);
    if (object == NULL){
        return NULL;
    }

    object -> type = PHYLIB_ROLLING_BALL;
    object->obj.rolling_ball.number = number;
    if (pos == NULL || vel == NULL || acc == NULL){
        return NULL;
    }
    
    object->obj.rolling_ball.pos = *pos;
    object->obj.rolling_ball.vel = *vel;
    object->obj.rolling_ball.acc = *acc;


    return object;
}

/*make new hole for table given position coords.*/
phylib_object *phylib_new_hole( phylib_coord *pos ){

    phylib_object * object = malloc(sizeof(phylib_object));
    //printf("MALLOC'D HOLE @ %p\n", (void *)object);
    if (object == NULL){
        return NULL;
    }

    object -> type = PHYLIB_HOLE;
    if (pos == NULL){
        return NULL;
    }
    object->obj.hole.pos = *pos;

    return object;
}

phylib_object *phylib_new_hcushion( double y ){

    phylib_object * object = malloc(sizeof(phylib_object));
    //printf("MALLOC'D HCUSHION @ %p\n", (void *)object);
    if (object == NULL){
        return NULL;
    }

    object -> type = PHYLIB_HCUSHION;
    object->obj.hcushion.y = y;

    return object;
}

phylib_object *phylib_new_vcushion( double x ){

    phylib_object * object = malloc(sizeof(phylib_object));
    //printf("MALLOC'D VCUSHION @ %p\n", (void *)object);
    if (object == NULL){
        return NULL;
    }

    object -> type = PHYLIB_VCUSHION;
    object->obj.vcushion.x = x;

    return object;
}

/*make and initialize new table for game*/
phylib_table *phylib_new_table( void ){

    phylib_table * table = malloc(sizeof(phylib_table));
    //printf("MALLOC'D TABLE @ %p\n", (void *)table);
    if (table == NULL){
        return NULL;
    }

    //set time to zero
    table -> time = 0.0;

    //add new objects to table
    table->object[0]=phylib_new_hcushion(0.0);
    table->object[1]=phylib_new_hcushion(PHYLIB_TABLE_LENGTH);
    
    table->object[2]=phylib_new_vcushion(0.0);
    table->object[3]=phylib_new_vcushion(PHYLIB_TABLE_WIDTH);

    //set coords to be used for the holes
    phylib_coord top_left;
    top_left.x = 0.0;
    top_left.y = 0.0;

    phylib_coord top_right;
    top_right.x = PHYLIB_TABLE_WIDTH;
    top_right.y = 0.0;

    phylib_coord mid_left;
    mid_left.x = 0.0;
    mid_left.y = (PHYLIB_TABLE_LENGTH/2);

    phylib_coord mid_right;
    mid_right.x = PHYLIB_TABLE_WIDTH;
    mid_right.y = (PHYLIB_TABLE_LENGTH/2);

    phylib_coord bottom_left;
    bottom_left.x = 0.0;
    bottom_left.y = PHYLIB_TABLE_LENGTH;

    phylib_coord bottom_right;
    bottom_right.x = PHYLIB_TABLE_WIDTH;
    bottom_right.y = PHYLIB_TABLE_LENGTH;

    //add holes to table
    table->object[4]=phylib_new_hole(&top_left);
    table->object[5]=phylib_new_hole(&mid_left);
    table->object[6]=phylib_new_hole(&bottom_left);
    table->object[7]=phylib_new_hole(&top_right);
    table->object[8]=phylib_new_hole(&mid_right);
    table->object[9]=phylib_new_hole(&bottom_right);

    //check if objects that were just initialized are null, returning null if they are
    for (int i = 0; i < 10; i++){
        if (table->object[i] == NULL){
            return NULL;
        }
    }

    //otherwise set rest of elements to null
    for (int i = 10; i < 26; i++){
        table->object[i] = NULL;
    }
    
    return table;
}

/*copy object in src into dest*/
void phylib_copy_object( phylib_object **dest, phylib_object **src ){

    /*set desitination to null if source is null, otherwise
    malloc memory for a new object and memcpy data from src
    to dest*/
    if (*src == NULL){
        *dest = NULL;
    }else{
        phylib_object * object = malloc(sizeof(phylib_object));
        //printf("MALLOC'D COPY OF OBJECT @ %p\n", (void *)object);
        *dest = object;
        memcpy(*dest, *src, sizeof(phylib_object));
    }
}

phylib_table *phylib_copy_table( phylib_table *table ){

    phylib_table * table_copy = malloc(sizeof(phylib_table));
    //printf("MALLOC'D COPY OF TABLE @ %p\n", (void *)table_copy);
    if (table_copy == NULL){
        return NULL;
    }

    /*copy all attributes including time and objects from table
    into table_copy*/
    table_copy->time = table->time;

    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++){
        phylib_copy_object(&table_copy->object[i], &table->object[i]);
    }

    return table_copy;
}

void phylib_add_object( phylib_table *table, phylib_object *object ){

    /*check through objects not initialled during creation
    to find a space for the new object, when found add the object
    and then break so object is only added once*/
    for (int i = 10; i < PHYLIB_MAX_OBJECTS; i++){
        if (table->object[i] == NULL){
            table->object[i] = object;
            break;
        }
    }
}

void phylib_free_table( phylib_table *table ){

    //free all objects in the table then the table itself
    //set everything to null after they are free'd
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++){
        //printf("OBJECT FREE'D @ %p\n", (void *)table->object[i]);
        free(table->object[i]);
        table->object[i] = NULL;
    }
    //printf("TABLE FREE'D @ %p\n", (void *)table);
    free(table);
    table = NULL;
}

phylib_coord phylib_sub(phylib_coord c1, phylib_coord c2 ){

    //create new coord thats the diff between the two coords and return
    phylib_coord sub;
    sub.x = (c1.x - c2.x);
    sub.y = (c1.y - c2.y);
    return sub;
}

double phylib_length( phylib_coord c ){

    return sqrt((c.x * c.x) + (c.y * c.y));
}

double phylib_dot_product( phylib_coord a, phylib_coord b ){

    return ((a.x * b.x) + (a.y * b.y));
}

/*calculates the distance between a rolling ball and different
types of objects on the table*/
double phylib_distance( phylib_object *obj1, phylib_object *obj2 ){

    double distance = 0.0;
    phylib_coord sub;

    //check if obj1 is a rolling ball
    if (obj1->type != 1){
        return -1.0;
    }

    //otherwise, check distance between rolling ball and object using sub and length functions
    if (obj2->type == 0){
        sub = phylib_sub(obj1->obj.rolling_ball.pos, obj2->obj.still_ball.pos);
        distance = phylib_length(sub) - (PHYLIB_BALL_DIAMETER);
    }else if (obj2->type == 1){
        sub = phylib_sub(obj1->obj.rolling_ball.pos, obj2->obj.rolling_ball.pos);
        distance = phylib_length(sub) - (PHYLIB_BALL_DIAMETER);
    }else if (obj2->type == 2){
        sub = phylib_sub(obj1->obj.rolling_ball.pos, obj2->obj.hole.pos);
        distance = phylib_length(sub) - (PHYLIB_HOLE_RADIUS);
    }else if (obj2->type == 3){
        double cushion = obj2->obj.hcushion.y;
        double d1 = fabs(obj1->obj.rolling_ball.pos.y - cushion);
        distance = d1 -PHYLIB_BALL_RADIUS;
    }else if (obj2->type == 4){
        double cushion = obj2->obj.vcushion.x;
        double d1 = fabs(obj1->obj.rolling_ball.pos.x - cushion);
        distance = d1 -PHYLIB_BALL_RADIUS;
    }else{
        return -1.0;
    }
    return distance;
}

/*to roll the ball, take the old ball and calc position and velocity
changes and apply them to the new ball*/
void phylib_roll( phylib_object *new, phylib_object *old, double time ){

    if (new->type == 1 && old->type == 1){

        //calculate x pos change
        double term2_x = (old->obj.rolling_ball.vel.x * time);
        double term3_x = (0.5 * old->obj.rolling_ball.acc.x * (time*time));
        new->obj.rolling_ball.pos.x = fabs(old->obj.rolling_ball.pos.x + term2_x + term3_x);

        //calcualte y pos change
        double term2_y = (old->obj.rolling_ball.vel.y * time);
        double term3_y = (0.5 * old->obj.rolling_ball.acc.y * (time*time));
        new->obj.rolling_ball.pos.y = fabs(old->obj.rolling_ball.pos.y + term2_y + term3_y);

        //calculate new velocity in x
        new->obj.rolling_ball.vel.x = old->obj.rolling_ball.vel.x + (old->obj.rolling_ball.acc.x * time);
        //calculate new velocity in y
        new->obj.rolling_ball.vel.y = old->obj.rolling_ball.vel.y + (old->obj.rolling_ball.acc.y * time);

        //check for if velocities change sign
        double vel_x_check = (old->obj.rolling_ball.vel.x * new->obj.rolling_ball.vel.x);
        double vel_y_check = (old->obj.rolling_ball.vel.y * new->obj.rolling_ball.vel.y);

        if (vel_x_check < 0){
            new->obj.rolling_ball.vel.x = 0.0;
            new->obj.rolling_ball.acc.x = 0.0;
        }
        if (vel_y_check < 0){
            new->obj.rolling_ball.vel.y = 0.0;
            new->obj.rolling_ball.acc.y = 0.0;
        }

        // double speed = phylib_length(new->obj.rolling_ball.vel);
        // if (speed > PHYLIB_VEL_EPSILON){
        //     new->obj.rolling_ball.acc.x = (-1.0 * new->obj.rolling_ball.vel.x) / speed * PHYLIB_DRAG;
        //     new->obj.rolling_ball.acc.y = (-1.0 * new->obj.rolling_ball.vel.y) / speed * PHYLIB_DRAG;
        // }
    }
}

/*check if the rolling ball has slowed enough to be considered stopped*/
unsigned char phylib_stopped( phylib_object *object ){

    double speed = phylib_length(object->obj.rolling_ball.vel);
    
    //if speed is slow enough, convert rolling ball into still ball
    if (speed < PHYLIB_VEL_EPSILON){
        
        unsigned char number = object->obj.rolling_ball.number;
        double x = object->obj.rolling_ball.pos.x;
        double y = object->obj.rolling_ball.pos.y;

        object->type = PHYLIB_STILL_BALL;
        object->obj.still_ball.number = number;
        object->obj.still_ball.pos.x = x;
        object->obj.still_ball.pos.y = y;

        //printf("STOPPED\n");

        return 1;
    }

    return 0;

}

/*bounce rolling ball off different types of objects*/
void phylib_bounce( phylib_object **a, phylib_object **b ){

    unsigned char number = (*b)->obj.still_ball.number;
    double x = (*b)->obj.still_ball.pos.x;
    double y = (*b)->obj.still_ball.pos.y;
    phylib_coord r_ab;
    
    switch ((*b)->type){

        case PHYLIB_HCUSHION:
            //printf("BOUNCE--HCUSHION\n");
            //negate x coords of velocity and acceleration
            (*a)->obj.rolling_ball.vel.y = (-1.0 * (*a)->obj.rolling_ball.vel.y);
            (*a)->obj.rolling_ball.acc.y = (-1.0 * (*a)->obj.rolling_ball.acc.y);
            break;

        case PHYLIB_VCUSHION:
            //negate x coords of velocity and acceleration
            //printf("BOUNCE--VCUSHION\n");
            (*a)->obj.rolling_ball.vel.x = (-1.0 * (*a)->obj.rolling_ball.vel.x);
            (*a)->obj.rolling_ball.acc.x = (-1.0 * (*a)->obj.rolling_ball.acc.x);
            //printf("HEY!!");
            break;

        case PHYLIB_HOLE:
            //printf("BOUNCE--HOLE\n");
            //free ball from table
            //printf("BOUNCE: FREE'D @ %p\n", (void *)(*a));
            free(*a);
            (*a) = NULL;
            break;
        
        case PHYLIB_STILL_BALL:
            //convert still ball into rolling ball then continue to next case
            //printf("BOUNCE--STILL_BALL\n");
            (*b)->type = PHYLIB_ROLLING_BALL;
            (*b)->obj.rolling_ball.number = number;
            (*b)->obj.rolling_ball.pos.x = x;
            (*b)->obj.rolling_ball.pos.y = y;
            (*b)->obj.rolling_ball.vel.x = 0.0;
            (*b)->obj.rolling_ball.vel.y = 0.0;
            (*b)->obj.rolling_ball.acc.x = (*a)->obj.rolling_ball.acc.x;
            (*b)->obj.rolling_ball.acc.y = (*a)->obj.rolling_ball.acc.y;
        
        case PHYLIB_ROLLING_BALL:
            //printf("BOUNCE--ROLLING_BALL\n");
            //Compute the position of a with respect to b: subtract the position of b from a
            r_ab = phylib_sub((*a)->obj.rolling_ball.pos, (*b)->obj.rolling_ball.pos);
            //Compute the relative velocity of a with respect to b: subtract the velocity of b from a
            phylib_coord v_rel = phylib_sub((*a)->obj.rolling_ball.vel, (*b)->obj.rolling_ball.vel);
            //Divide the x and y components of r_ab by the length of r_ab
            double r_ab_length = phylib_length(r_ab);
            phylib_coord n;
            n.x = (r_ab.x / r_ab_length);
            n.y = (r_ab.y / r_ab_length);
            //Calculate the ratio of the relative velocity, v_rel, in the direction of ball a by computing the dot_product of v_rel with respect to n; call that v_rel_n.
            double v_rel_n = phylib_dot_product(v_rel, n);
            /*Update the x velocity of ball a by subtracting v_rel_n multipied by the x component of
            vector n. Similarly, Update the y velocity of ball a by subtracting v_rel_n multipied by
            the y component of vector n*/
            phylib_coord term;
            term.x = (v_rel_n * n.x);
            term.y = (v_rel_n * n.y);
            (*a)->obj.rolling_ball.vel = phylib_sub((*a)->obj.rolling_ball.vel, term);
            //Update the x and y velocities of ball b by adding the product of v_rel_n and vector n
            (*b)->obj.rolling_ball.vel.x += (v_rel_n * n.x);
            (*b)->obj.rolling_ball.vel.y += (v_rel_n * n.y);
            /*Compute the speed of a and b as the lengths of their velocities. If the speed is greater
            than PHYLIB_VEL_EPSILON then set the acceleration of the ball to the negative
            velocity divided by the speed multiplied by PHYLIB_DRAG.*/
            double speed_a = phylib_length((*a)->obj.rolling_ball.vel);
            double speed_b = phylib_length((*b)->obj.rolling_ball.vel);
            if (speed_a > PHYLIB_VEL_EPSILON || speed_b > PHYLIB_VEL_EPSILON){
                (*a)->obj.rolling_ball.acc.x = (-1.0 * (*a)->obj.rolling_ball.vel.x) / speed_a * PHYLIB_DRAG;
                (*a)->obj.rolling_ball.acc.y = (-1.0 * (*a)->obj.rolling_ball.vel.y) / speed_a * PHYLIB_DRAG;
                (*b)->obj.rolling_ball.acc.x = (-1.0 * (*b)->obj.rolling_ball.vel.x) / speed_b * PHYLIB_DRAG;
                (*b)->obj.rolling_ball.acc.y = (-1.0 * (*b)->obj.rolling_ball.vel.y) / speed_b * PHYLIB_DRAG;
            }
            break;
    }
}

/*check how many balls are rolling*/
unsigned char phylib_rolling( phylib_table *t ){

    unsigned char num_rolling = 0;

    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++){
        if (t->object[i] != NULL){
            if (t->object[i]->type == 1){
                num_rolling +=1;
            }
        }
    }
    return num_rolling;
}

/*create segments of a shot by copying the table and making a new copy
every time a rolling ball comes into contact with another object,
if the rolling ball has slowed to a stop, or if there are no more rolling balls
on the table*/
phylib_table *phylib_segment( phylib_table *table ){

    //check how many rolling balls there are
    if (phylib_rolling(table) == 0){
        return NULL;
    }

    //copy table
    phylib_table *copy_table = phylib_copy_table(table);
    if (copy_table == NULL){
        return NULL;
    }

    double time = 0.0; 
    //loop through at pace of sim rate, maxing out at 10minutes
    for (time = PHYLIB_SIM_RATE; time <= PHYLIB_MAX_TIME; time += PHYLIB_SIM_RATE){
        //loop through balls on table
        for (int i = 10; i < PHYLIB_MAX_OBJECTS; i++){
            //check for rolling balls
            if (copy_table->object[i] != NULL && copy_table->object[i]->type == PHYLIB_ROLLING_BALL){
                //roll the rolling balls
                phylib_roll(copy_table->object[i], table->object[i], time);
                //check if the rolling ball has stopped
                if (phylib_stopped(copy_table->object[i])){
                    copy_table->time += time;
                    return copy_table;
                }
            }
        }
        //check through the rest of the objects on the table to sense for collisions
        for (int i = 10; i < PHYLIB_MAX_OBJECTS; i++){
            if (copy_table->object[i] != NULL && copy_table->object[i]->type == PHYLIB_ROLLING_BALL){
                for (int j = 0; j < PHYLIB_MAX_OBJECTS; j++){
                    if (copy_table->object[j] != NULL && i != j){
                        double distance = (phylib_distance(copy_table->object[i], copy_table->object[j]));
                        //if a collision occurs apply bounce function and return segment of the table
                        if ( distance < 0.0){
                            //need to apply phylib_bounce here
                            phylib_bounce(&copy_table->object[i], &copy_table->object[j]);
                            copy_table->time += time;
                            return copy_table;
                        }
                    }
                }
            }
        }
    }

    //otherwise return table
    return copy_table;

}

char *phylib_object_string( phylib_object *object ){
    static char string[80];
    if (object==NULL){
        snprintf( string, 80, "NULL;" );
        return string;
    }

    switch (object->type){
        case PHYLIB_STILL_BALL:
            snprintf( string, 80,
            "STILL_BALL (%d,%6.1lf,%6.1lf)",
            object->obj.still_ball.number,
            object->obj.still_ball.pos.x,
            object->obj.still_ball.pos.y );
            break;
        case PHYLIB_ROLLING_BALL:
            snprintf( string, 80,
            "ROLLING_BALL (%d,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf)",
            object->obj.rolling_ball.number,
            object->obj.rolling_ball.pos.x,
            object->obj.rolling_ball.pos.y,
            object->obj.rolling_ball.vel.x,
            object->obj.rolling_ball.vel.y,
            object->obj.rolling_ball.acc.x,
            object->obj.rolling_ball.acc.y );
            break;
        case PHYLIB_HOLE:
            snprintf( string, 80,
            "HOLE (%6.1lf,%6.1lf)",
            object->obj.hole.pos.x,
            object->obj.hole.pos.y );
            break;
        case PHYLIB_HCUSHION:
            snprintf( string, 80,
            "HCUSHION (%6.1lf)",
            object->obj.hcushion.y );
            break;
        case PHYLIB_VCUSHION:
            snprintf( string, 80,
            "VCUSHION (%6.1lf)",
            object->obj.vcushion.x );
            break;
    }
    return string;
}
