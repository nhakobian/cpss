<div class=browser_error style="%(errorsty)s">%(error)s</div>

<center>
   <h1>User Information</h1>

   <table>
      <tr>
        <td>
          Name:
        </td>
        <td>
          %(name)s
        </td>
      </tr>

      <tr>
        <td>
          Email:
        </td>
        <td>
          %(email)s
        </td>
      </tr>
   </table>
</center>

<br>

<center>
   <form action="user/" method="post">
   <table>
      <tr>
        <td colspan=2>
          <h3>Change Password</h3>
        </td>
      </tr>
      
      <tr>
        <td>
          Old Password:
        </td>
        <td>
          <input type=password name="oldpw">
        </td>
      </tr>

      <tr>
        <td>
          New Password:
        </td>
        <td>
          <input type=password name="newpw1">
        </td>
      </tr>

      <tr>
        <td>
          Repeat New Password:
        </td>
        <td>
          <input type=password name="newpw2">
        </td>
      </tr>

      <tr>
        <td colspan=2>
          <center>
            <input type=submit name="changepw" value="Change Password">
          </center>
        </td>
      </tr>
   </table>
   </form>
</center>
