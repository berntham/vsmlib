#include <fstream>
#include <algorithm>
#include <locale>
#include <codecvt>
#include "string_tools.hpp"

//#if !defined(MAX_STR_SIZE)
//#define MAX_STR_SIZE  1500
//#endif
//const char separators[]=" .,:;!?()[]-\t\"'";

  
std::string wstring_to_utf8 (const std::wstring& str)
{
    std::wstring_convert<std::codecvt_utf8<wchar_t>> myconv;
    return myconv.to_bytes(str);
}

inline void trim3(std::wstring & str)
{
  //str.erase(str.begin(), find_if(str.begin(), str.end(), [](char& ch)->bool { return !isspace(ch); }));
  //str.erase(find_if(str.rbegin(), str.rend(), [](char& ch)->bool { return !isspace(ch); }).base(), str.end());
  //for (unsigned int i=0;i<str.length();i++)
  //{
  //	if (!isalpha(str[i])) str[i]='_';
  //}
   //return str;
}  

inline void clean(std::wstring & str)
{
      trim3(str);
      std::transform(str.begin(), str.end(), str.begin(), ::tolower);
}



bool is_line_valid(std::string const & w)
{
  if (w.length()==0) return false;
  if ((w[0])=='<') return false;
  return true;
}

bool hasEnding (std::string const &fullString, std::string const &ending)
{
    if (fullString.length() >= ending.length()) {
        return (0 == fullString.compare (fullString.length() - ending.length(), ending.length(), ending));
    } else {
        return false;
    }
}

std::list<std::wstring> load_words(std::string name_file)
{
  std::wifstream d_file(name_file);
  d_file.imbue(std::locale("en_US.UTF8"));
  std::wstring line;
  std::list<std::wstring> result;
  while( std::getline( d_file, line ) ) 
    {
        trim3(line);
        result.push_back(line);
    }
    return result;
}