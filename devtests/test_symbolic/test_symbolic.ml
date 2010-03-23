(* In the following we will test the functions to add, multiply, differentiate,
integrate and integrate femfuns over surfaces, which are defined in fem_element.ml.
A femfun can be expressed as a polynomial in the shape functions L1,L2,..,Ln  
and the usual rules for operations on polynomials are extended to such functions.

NOTE - to be executed from **inside fem_element directory**
*)

#use "ng_load.ml";;

(* first femfun to use in the following tests *)
let test1 =  [|{ff_coefficient = 2.; 
		ff_dL_powers = [|{dlp_nr_L = 0; dlp_nr_dx = 0; dlp_pow = 1};{dlp_nr_L = 1; dlp_nr_dx = 2; dlp_pow = 2}|]; 
		ff_L_powers = [|4; 3; 2; 1|]}|]
;;

(* Printf.printf "%s\n" (femfun_to_string test1 );; *)

(* second femfun to use in the following tests *)
let test2 =  [|{ff_coefficient = 10.;
		ff_dL_powers = [|{dlp_nr_L = 0; dlp_nr_dx = 0; dlp_pow = 1}|];
		ff_L_powers = [|3; 1; 0; 0|]}|]
;;		

(* Printf.printf "%s\n" (femfun_to_string test1 );; *)

(* third femfun to use in the following tests *)
let test3 =  [|{ff_coefficient = 1.; ff_dL_powers = [||]; ff_L_powers = [|0; 0; 0; 2|]};
	       {ff_coefficient = -1.; ff_dL_powers = [||]; ff_L_powers = [|0; 0; 1; 1|]};
	       {ff_coefficient = -1.; ff_dL_powers = [||]; ff_L_powers = [|0; 1; 0; 1|]};
	       {ff_coefficient = -1.; ff_dL_powers = [||]; ff_L_powers = [|1; 0; 0; 1|]}|]
;;

(* Printf.printf "%s\n" (femfun_to_string test3 );; *)

let starting_lines =
  Printf.printf "\n****  ****  ****  ****  ****  ****  ****  ****  ****  ****\n\n"  
;;

(* function to test the sum of two femfun *)
let test_sum s1 s2 f1 f2 known_result =
  let () = Printf.printf "%s\n" "begin test femfun_add" in
  let ident =
    if f1 = f2
    then "equal"
    else "not equal"
  in
  let () = Printf.printf "the test functions f1 and f2 are %s \n" ident in
  let result = femfun_add ~scale1:s1 ~scale2:s2 f1 f2 in
  let () = Printf.printf "%f * %s\n" (s1) (femfun_to_string f1 ) in
  let () = Printf.printf "%f * %s\n" (s2) (femfun_to_string f2 ) in
  let () = Printf.printf "%s\n" (femfun_to_string result ) in
  
  let () = Printf.printf("The test on sum is %s\n") (string_of_bool (result = known_result))
  in ()
;;

(* test the sum of two equal femfun *)
test_sum 2.0 3.0 test1 test1 [|{ff_coefficient = 10.;
				ff_dL_powers =
				[|{dlp_nr_L = 0; dlp_nr_dx = 0; dlp_pow = 1};
				  {dlp_nr_L = 1; dlp_nr_dx = 2; dlp_pow = 2}|];
				ff_L_powers = [|4; 3; 2; 1|]}|]
;;


(* test the sum of two different femfun *)
test_sum 2.0 3.0 test1 test2 [|{ff_coefficient = 4.;
				ff_dL_powers =
				[|{dlp_nr_L = 0; dlp_nr_dx = 0; dlp_pow = 1};
				  {dlp_nr_L = 1; dlp_nr_dx = 2; dlp_pow = 2}|];
				ff_L_powers = [|4; 3; 2; 1|]};
			       {ff_coefficient = 30.;
				ff_dL_powers = [|{dlp_nr_L = 0; dlp_nr_dx = 0; dlp_pow = 1}|];
				ff_L_powers = [|3; 1; 0; 0|]}|]
  
;;

(* function to test the multiplication of two femfun *)
let test_mult coeff f1 f2 known_result =
  let () = Printf.printf "%s\n" "begin test femfun_mult" in
  let result = femfun_mult f1 f2 coeff in
  let () = Printf.printf "%s\n" (femfun_to_string f1 ) in
  let () = Printf.printf "%s\n" (femfun_to_string f2 ) in
  let () = Printf.printf "%s\n" (femfun_to_string result ) in
  
  let () = Printf.printf("The test on multiplication is %s\n") (string_of_bool (result = known_result))
  in ()
;;

(* test multiplication of two single-addend femfuns *)
test_mult 1.0 test1 test2 [|{ff_coefficient = 20.;
			     ff_dL_powers =
			     [|{dlp_nr_L = 0; dlp_nr_dx = 0; dlp_pow = 2};
			       {dlp_nr_L = 1; dlp_nr_dx = 2; dlp_pow = 2}|];
			     ff_L_powers = [|7; 4; 2; 1|]}|]
;;


(* test multiplication of multi-addend femfuns *)
test_mult 1.0 test1 test3 [|{ff_coefficient = -2.;
			     ff_dL_powers =
			     [|{dlp_nr_L = 0; dlp_nr_dx = 0; dlp_pow = 1};
			       {dlp_nr_L = 1; dlp_nr_dx = 2; dlp_pow = 2}|];
			     ff_L_powers = [|4; 3; 3; 2|]};
			    {ff_coefficient = -2.;
			     ff_dL_powers =
			     [|{dlp_nr_L = 0; dlp_nr_dx = 0; dlp_pow = 1};
			       {dlp_nr_L = 1; dlp_nr_dx = 2; dlp_pow = 2}|];
			     ff_L_powers = [|4; 4; 2; 2|]};
			    {ff_coefficient = -2.;
			     ff_dL_powers =
			     [|{dlp_nr_L = 0; dlp_nr_dx = 0; dlp_pow = 1};
			       {dlp_nr_L = 1; dlp_nr_dx = 2; dlp_pow = 2}|];
			     ff_L_powers = [|5; 3; 2; 2|]};
			    {ff_coefficient = 2.;
			     ff_dL_powers =
			     [|{dlp_nr_L = 0; dlp_nr_dx = 0; dlp_pow = 1};
			       {dlp_nr_L = 1; dlp_nr_dx = 2; dlp_pow = 2}|];
			     ff_L_powers = [|4; 3; 2; 3|]}|]
;;

(* function to test the differentiation of a femfun with respect to a variable x *)
let test_differen f1 nr_dx known_result =
  let () = Printf.printf "%s\n" "begin test femfun_diff_x" in
  let result = femfun_diff_x f1 nr_dx in
  let () = Printf.printf "%s\n" (femfun_to_string f1 ) in
  let () = Printf.printf "%s\n" (femfun_to_string result ) in

  let () = Printf.printf("The test on differentiation is %s\n") (string_of_bool (result = known_result))
  in ()
;;

(* test the differentiation of a femfun with respect to a variable *)
test_differen  test3 2 [|{ff_coefficient = -1.;
			  ff_dL_powers = [|{dlp_nr_L = 0; dlp_nr_dx = 2; dlp_pow = 1}|];
			  ff_L_powers = [|0; 0; 0; 1|]};
			 {ff_coefficient = -1.;
			  ff_dL_powers = [|{dlp_nr_L = 1; dlp_nr_dx = 2; dlp_pow = 1}|];
			  ff_L_powers = [|0; 0; 0; 1|]};
			 {ff_coefficient = -1.;
			  ff_dL_powers = [|{dlp_nr_L = 2; dlp_nr_dx = 2; dlp_pow = 1}|];
			  ff_L_powers = [|0; 0; 0; 1|]};
			 {ff_coefficient = -1.;
			  ff_dL_powers = [|{dlp_nr_L = 3; dlp_nr_dx = 2; dlp_pow = 1}|];
			  ff_L_powers = [|0; 0; 1; 0|]};
			 {ff_coefficient = -1.;
			  ff_dL_powers = [|{dlp_nr_L = 3; dlp_nr_dx = 2; dlp_pow = 1}|];
			  ff_L_powers = [|0; 1; 0; 0|]};
			 {ff_coefficient = -1.;
			  ff_dL_powers = [|{dlp_nr_L = 3; dlp_nr_dx = 2; dlp_pow = 1}|];
			  ff_L_powers = [|1; 0; 0; 0|]};
			 {ff_coefficient = 2.;
			  ff_dL_powers = [|{dlp_nr_L = 3; dlp_nr_dx = 2; dlp_pow = 1}|];
			  ff_L_powers = [|0; 0; 0; 1|]}|]
;;

(* function to test the integration of a femfun with respect to a shape function L *)
let test_integrate f1 nr_L known_result =
  let () = Printf.printf "%s\n" "begin test femfun_integrate" in
  let result =  femfun_integrate f1 nr_L in
  let () = Printf.printf "%s\n" (femfun_to_string f1 ) in
  let () = Printf.printf "%s\n" (femfun_to_string result ) in

  let () = Printf.printf("The test on integration is %s\n") (string_of_bool (result = known_result))
  in ()
;;


(* test the integration of a femfun with respect to a shape function L *)
test_integrate test3 1 [|{ff_coefficient = -1.; ff_dL_powers = [||]; ff_L_powers = [|0; 1; 1; 1|]};
			 {ff_coefficient = -1.; ff_dL_powers = [||]; ff_L_powers = [|1; 1; 0; 1|]};
			 {ff_coefficient = -0.5; ff_dL_powers = [||]; ff_L_powers = [|0; 2; 0; 1|]};
			 {ff_coefficient = 1.; ff_dL_powers = [||]; ff_L_powers = [|0; 1; 0; 2|]}|]
;;


(* function to test the integration of a femfun over a surface *)
let test_integrate_over_surface dim f1 nr_L known_result =
  let () = Printf.printf "%s\n" "begin test femfun_integrate_over_surface" in
  let result =   femfun_integrate_over_surface  dim f1 nr_L in
  let () = Printf.printf "%s\n" (femfun_to_string f1 ) in
  let extract_result = 
    match result with 
    | (nr_to_kill, integrating_Ls, result) -> result 
  in
  let () = Printf.printf "%s\n" (femfun_to_string extract_result) in
  
  let () = Printf.printf("The test on integration over a surface is %s\n") (string_of_bool (result = known_result))
  in result
;;


(* element defined on a 3-D space with 1 degree of freedom *)
let tetra = make_element 3 "X" 1 [||];;

(* femfun associated to a vertex of a tetrahedron *)
let l_3 = tetra.el_dof_funs.(0);;

(* Printf.printf "%s\n" (femfun_to_string L3);; *)
  

(* test the integration of a femfun over a surface of the tetrahedron *)
test_integrate_over_surface 3 l_3 1 (0, [|2; 3|],
				     [|{ff_coefficient = 0.16666666666666663; ff_dL_powers = [||];
					ff_L_powers = [|0; 0; 0; 0|]}|])
;;
